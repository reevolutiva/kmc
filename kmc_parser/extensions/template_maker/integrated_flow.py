from kmc_parser import (
    KMCParser, 
    registry, 
    plugin_manager, 
    ContextHandler, 
    MetadataHandler,
    GenerativeHandler,
    context_handler,
    metadata_handler,
    generative_handler,
    KMCPlugin
)

from kmc_parser.handlers.context.project import ProjectHandler
from kmc_parser.handlers.metadata.doc import DocumentMetadataHandler

class KMC_Parser_TemplateMaker():
    
    """
    Clase para crear plantillas de KMC Parser.
    
    Esta clase se encarga de crear plantillas para el KMC Parser utilizando
    la configuración proporcionada.
    """
    
    def __init__(self, project_data=None, doc_data=None):
        self.kmc_parser = KMCParser()
        self.project_data = project_data
        self.doc_data = doc_data
     
  
   
    def parse(self, markdown: str ) -> str:
        """
        Parse the KMC Parser and return the template.
        """
        # Crear una nueva instancia de parser para este ejemplo
        parser = self.kmc_parser
        
        from kmc_parser.extensions.template_maker.template_maker import KMC_TemplateMakerPlugin
        template_maker_plugin = KMC_TemplateMakerPlugin()
        plugin_manager.register_plugin(template_maker_plugin)
        
        project_config = {
            "project_data": self.project_data
        }
        
        doc_config = {
            "metadata": self.doc_data
        }
            
        registry.register_context_handler("project", ProjectHandler(config=project_config))
        registry.register_context_handler("doc", DocumentMetadataHandler(config=doc_config))

        
        resultado = parser.process_document(markdown_content=markdown)
        
        #resultado = parser.process_document(markdown_content=first_parse)
        
        return resultado
    
    