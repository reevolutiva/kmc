import logging
import sys
import os
import time

import llama_index # Línea 11 - donde se importa llama_index

# Importaciones actualizadas según la nueva estructura de LlamaIndex
from llama_index.core import SimpleDirectoryReader, Document, StorageContext, VectorStoreIndex
from llama_index.vector_stores.supabase import SupabaseVectorStore
from llama_index.core.vector_stores import MetadataFilters, ExactMatchFilter
import textwrap
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
from llama_index.core import Settings
from supabase import create_client, Client

# Usar os.environ.get con valores predeterminados para las pruebas
llm = AzureOpenAI(
    model=os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4"),
    deployment_name=os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4"),
    api_key=os.environ.get("AZURE_OPENAI_KEY", "test-key"),
    azure_endpoint=os.environ.get("AZURE_OPENAI_BASE", "https://example.openai.azure.com"),
    api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2024-02-01"),
)

# También modificar el modelo de embedding
embed_model = AzureOpenAIEmbedding(
    model=os.environ.get("AZURE_OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
    deployment_name=os.environ.get("AZURE_OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
    api_key=os.environ.get("AZURE_OPENAI_KEY", "test-key"),
    azure_endpoint=os.environ.get("AZURE_OPENAI_BASE", "https://example.openai.azure.com"),
    api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2024-02-01"),
)

Settings.llm = llm
Settings.embed_model = embed_model

class SupaBasePosgresMiddleware:
    
    def __init__(self):
        self.host: str = os.environ.get("MIDDLEWARE_SUPABASE_POSGRESS", "127.0.0.1")
        self.port: str = os.environ.get("MIDDLEWARE_SUPABASE_POSGRESS_PORT", "5432")
        self.user: str = os.environ.get("MIDDLEWARE_SUPABASE_POSGRESS_USERNAME", "postgres")
        self.password: str = os.environ.get("MIDDLEWARE_SUPABASE_POSGRESS_PASSWORD", "postgres")
        self.database: str = "postgres"
      
    def get_url( self ):
        """
        Get the URL of the Supabase instance.
        """
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
    


class SupabaseMiddleware:
    
    def build_url( self ):
        domain =  os.environ.get("MIDDLEWARE_SUPABASE_URL", "127.0.0.1") 
        port = os.environ.get("MIDDLEWARE_SUPABASE_PORT", "5432")
        url = f"http://{domain}:{port}"
        return url
    
    def get_client( self ):
        """
        Get the Supabase client.
        """
        supabase_url =  self.build_url()
        supabase: Client = create_client(supabase_url, os.environ.get("MIDDLEWARE_SUPABASE_ANON_KEY", "") )    
        
        return supabase


class LlamaIndexMiddleware:
    """
    Middleware for LlamaIndex.
    """
    def __init__(self, directory: str = "/app/doc", collection_name: str = "base_demo" ):
        self.directory = directory
        self.documents = []
        self.collection_name = collection_name
        logging.info(f"LlamaIndexMiddleware initialized with directory: {self.directory}")

    def load_posgress_connection_string(self) -> str:
        """
        Load the PostgreSQL connection string from environment variables.
        """
        logging.info("Loading PostgreSQL connection string.")
        postgres_connection_string = SupaBasePosgresMiddleware().get_url()
        logging.info(f"PostgreSQL connection string loaded: {postgres_connection_string}")
        return postgres_connection_string
    
    def load_document( self, document_path, doc_id=None ):
        """
        Load documents from a directory.
        """
        logging.info(f"Loading documents from directory: {document_path}")
        from llama_index.core import Document
        
        input_documents = SimpleDirectoryReader(input_files=[document_path] ).load_data()
        
        if doc_id:
            
            documents = []
            for doc in input_documents:
                
                metadata = doc.metadata
                metadata["doc_id"] = doc_id
                
                new_doc = Document(
                    text=doc.text,
                    doc_id=doc_id,
                    hash=doc_id,
                    metadata=metadata
                )
                
                documents.append(new_doc)
                
            self.documents = documents
        else:
            self.documents = input_documents
        logging.info(f"Loaded {len(documents)} documents.")
        return documents
    
    def load_documents(self, directory: str):
        """
        Load documents from a directory.
        """
        logging.info(f"Loading documents from directory: {directory}")
        documents = SimpleDirectoryReader(directory).load_data()
        self.documents = documents
        logging.info(f"Loaded {len(documents)} documents.")
        return documents
    
    def get_index_from_db(self):
        """
        Retrieve an index from the database using embeddings stored in the vector store.
        """
        logging.info("Retrieving index from database.")
        postgres_connection_string = self.load_posgress_connection_string()
        logging.info(f"Using PostgreSQL connection string: {postgres_connection_string}")
        logging.info(f"Collection name: {self.collection_name}")
        
        vector_store = SupabaseVectorStore(
            postgres_connection_string=(
                postgres_connection_string
            ),
            collection_name=self.collection_name,
        )
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        index = VectorStoreIndex.from_vector_store(vector_store=vector_store, storage_context=storage_context)
        logging.info("Index retrieved successfully from database.")
        return index
    
    
    def semantic_chunking( self, documents: list ):
        
        from llama_index.core.node_parser import SemanticSplitterNodeParser       
        splitter = SemanticSplitterNodeParser(
            buffer_size=1, breakpoint_percentile_threshold=95, embed_model=embed_model
        )        
        nodes = splitter.get_nodes_from_documents(documents)
        
        return nodes
    
    
    def pipeline_igestion( self, vector_store , documents: list ):
        
        from llama_index.core.storage.docstore import SimpleDocumentStore
        from llama_index.core.ingestion import IngestionPipeline, DocstoreStrategy
        from llama_index.core.node_parser import SentenceSplitter
        
        logging.info("Starting ingestion pipeline.")
        
        before_nodes = self.semantic_chunking(documents)
        
        # Configurar el docstore
        docstore = SimpleDocumentStore()
    
        pipeline = IngestionPipeline(
            docstore=docstore,
            vector_store=vector_store,
            docstore_strategy=DocstoreStrategy.UPSERTS,
            transformations=[
                SentenceSplitter(),
                embed_model
            ]
        )
      
        storage_path = "/app/src/pipeline_storage"
        if os.path.exists(storage_path):
            logging.info(f"Storage directory already exists at: {storage_path}")
            pipeline.load(storage_path)
            
        nodes = pipeline.run(nodes=before_nodes)
        pipeline.persist(storage_path)
        
        return nodes

    def create_index(self, documents: list):
        """
        Create an index for the documents.
        """
        logging.info("Creating index for documents.")
        postgres_connection_string = self.load_posgress_connection_string()
        logging.info(f"Using PostgreSQL connection string: {postgres_connection_string}")
        logging.info(f"Collection name: {self.collection_name}")
        
        vector_store = SupabaseVectorStore(
            postgres_connection_string=(
                postgres_connection_string
            ),
            collection_name=self.collection_name,
        )

        
        nodes = self.pipeline_igestion(vector_store, documents)
        
        logging.info("Index created successfully.")
        return nodes
    
    def query_index_by_files(self, index, query: str, docs_id: list ):
        
        from llama_index.core.vector_stores import MetadataFilters, ExactMatchFilter
        
        filters = []
        for doc_id in docs_id:
            filters.append(ExactMatchFilter(key="doc_id", value=doc_id ))


        metadataFilters = MetadataFilters(
            filters=filters
        )

        queryEngine = index.as_query_engine(filters=metadataFilters)
        #queryEngine = index.as_query_engine()
        response = queryEngine.query(query)
        return response

    def query_index(self, index, query: str):
        """
        Query the index with a given query.
        """
        logging.info(f"Querying index with query: {query}")
        queryEngine = index.as_query_engine()
        response = queryEngine.query(query)
        logging.info(f"Query response: {response}")
        return response
    
    

    def agent_query(self, query: str):
        """
        Query the documents with a given query.
        """
        #logging.info(f"Agent query initiated with query: {query}")
        #documents = self.load_documents(self.directory)
        index = self.get_index_from_db()
        response = self.query_index(index, query)
        #logging.info(f"Agent query response: {response}")
        return response
    
    def files_agent_query(self, query: str, docs_id: list):
        """
        Query the documents with a given query.
        """
        index = self.get_index_from_db()
        print("docs_id:", docs_id)
        response = self.query_index_by_files(index, query, docs_id)
        print("Response:", response)

        if not response or response.response == "Empty Response":
            logging.info("Empty response from index query. Querying LLM directly.")
            response = llm.complete(prompt=query)
            print("LLM Response:", response)
            return response.text if hasattr(response, "text") else str(response)

        return response.response
    def get_path_supabase_storage(self, document: str, bucketName: str, original_path_document: str = None ):
        
        basename = os.path.basename(document)
        basename_whiout_extension = os.path.basename(original_path_document).split(".")[0]
        print("document:", original_path_document)
        print("Basename:", basename)
        print("Basename without extension:", basename_whiout_extension)
        supabase_storage = original_path_document.split(f"{bucketName}/")[1]
        supabase_storage = supabase_storage.split(basename_whiout_extension)[0]
        
        return supabase_storage, basename
    
    def download_document(self, document: str):
        """
        Download a document directly from the given URL and save it to the specified directory.
        Retries up to 5 times in case of HTTP errors.
        """
    
        supabase = SupabaseMiddleware().get_client()
        bucketName = "project-documents"
        attempts = 0
        max_attempts = 5
        
        supabase_storage, basename = self.get_path_supabase_storage( document, bucketName, document )
        
        docuemnt_to_download = document.split("project-documents/")[-1]
        logging.info(f"Downloading document: {document}")
        logging.info(f"Document to download: {docuemnt_to_download}")
        while attempts < max_attempts:
            
            logging.info(f"Attempting to download document (attempt {attempts + 1}/{max_attempts})")
            
            try:
                response = (
                    supabase.storage
                    .from_(bucketName)
                    .download(docuemnt_to_download)
                )
                with open(self.directory + f"/{basename}", "wb+") as f:
                    f.write(response)
                logging.info("Document downloaded successfully.")
                return self.directory + f"/{basename}"
            except Exception as e:
                attempts += 1
                logging.error(f"Error downloading document (attempt {attempts}/{max_attempts}): {e}")
                if attempts < max_attempts:
                    logging.info("Retrying in 1 second...")
                    time.sleep(1)

        logging.error(f"Failed to download document after {max_attempts} attempts. Returning the original URL.")
        return document
            
    def downlaod_docs( self, documents: list ):
        """
        Download documents to the specified directory.
        """
        
        supabase = SupabaseMiddleware().get_client()
        bucketName = "project-documents"
        
        logging.info(f"Downloading documents to directory: {self.directory}")
        for document in documents:
            logging.info(f"Downloading document: {document}")
            basename = os.path.basename(document)
            with open( self.directory + f"/{basename}" , "wb+") as f:
                response = (
                    supabase.storage
                    .from_(bucketName)
                    .download(document)
                )
        
                f.write(response)
        logging.info("Documents downloaded successfully.")
        
    def convert_pdf_to_md(self, pdf_file: str):
        """
        Convert a PDF file to Markdown format.
        """
        
        
        from markitdown import MarkItDown
        
        basename = os.path.basename(pdf_file)
        md_basename = basename.replace(".pdf", ".md")
        md_local_path = f"/app/doc/{md_basename}"
        
        md = MarkItDown()
        result = md.convert( pdf_file )
        content = result.text_content
        with open( md_local_path, "w") as f:
            f.write(content)
            
        return md_local_path
            
    def save_md_to_supabase(self, md_file: str ):
        """
        Save the Markdown file to Supabase storage.
        """
        supabase = SupabaseMiddleware().get_client()
        bucketName = "project-documents"
        
        supabase_storage, basename = self.get_path_supabase_storage(md_file, bucketName)
        
        with open(md_file, "rb") as f:
            response = (
                supabase.storage
                .from_(bucketName)
                .upload(f"{supabase_storage}/{basename}", f)
            )
        
        logging.info(f"Markdown file {basename} saved to Supabase storage.")
        
    def register_doc_id_in_doc_relation( self, doc_id: str, proyect_relation_id: str ):
        
        supabase = SupabaseMiddleware().get_client()
        try:
            response = supabase.table('project_document').update({
            "emmbeding_doc_id": doc_id
            }).eq('id', proyect_relation_id).execute()
            logging.info(f"Update successful: {response.data}")
        except Exception as e:
            logging.error(f"Error updating project_document: {e}")

    def llm_query(self, query: str):
        """
        Query the LLM with a given query.
        """
        logging.info(f"LLM query initiated with query: {query}")
        response = llm.complete(prompt=query)
        logging.info(f"LLM query response: {response}")
        return response.text