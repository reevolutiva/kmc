"""
Ejemplo de Plugin de LlamaIndex para KMC.

Este plugin demuestra la integración de LlamaIndex con KMC para buscar
información en una base de conocimiento y generar respuestas contextuales.
"""

import logging
from typing import Optional, Dict, Any

from llama_index.vector_stores.supabase import SupabaseVectorStore
from llama_index import VectorStoreIndex, SimpleDirectoryReader
from kmc_parser.extensions.plugin_base import KMCPlugin
from kmc_parser.core import registry

class LlamaIndexPlugin(KMCPlugin):
    """
    Plugin para integrar LlamaIndex con KMC.
    
    Este plugin permite realizar consultas a vectores de embeddings usando LlamaIndex
    y generar respuestas basadas en documentos y fuentes de conocimiento.
    """
    
    def __init__(self):
        """Inicializa el plugin de LlamaIndex."""
        super().__init__()
        self.index = None
        self.docs_path = None
        self.initialized = False
        
    def initialize(self) -> bool:
        """
        Inicializa el plugin registrando los handlers de LlamaIndex.
        
        Returns:
            bool: True si la inicialización fue exitosa.
        """
        self.logger.info("Inicializando LlamaIndex Plugin")
        
        # Registrar handler generativo para consultas de LlamaIndex
        registry.register_generative_handler("mcp:llamaindex", self.llamaindex_query_handler)
        
        self.initialized = True
        return True
        
    def setup_index(self, docs_path: str) -> bool:
        """
        Configura el índice de LlamaIndex con los documentos del directorio especificado.
        
        Args:
            docs_path: Ruta al directorio con los documentos para indexar
            
        Returns:
            bool: True si la configuración fue exitosa
        """
        try:
            self.logger.info(f"Configurando índice de LlamaIndex con documentos de: {docs_path}")
            self.docs_path = docs_path
            
            # Cargar documentos
            documents = SimpleDirectoryReader(docs_path).load_data()
            
            # Crear índice
            self.index = VectorStoreIndex.from_documents(documents)
            
            return True
        except Exception as e:
            self.logger.error(f"Error al configurar índice de LlamaIndex: {str(e)}")
            return False
    
    def llamaindex_query_handler(self, name: str, prompt: str, format_type: Optional[str] = None) -> str:
        """
        Handler generativo para consultas de LlamaIndex.
        
        Args:
            name: Nombre de la variable KMC
            prompt: Consulta para LlamaIndex
            format_type: Formato opcional para la respuesta
            
        Returns:
            str: Respuesta generada por LlamaIndex
        """
        try:
            if not self.index:
                return "ERROR: Índice de LlamaIndex no configurado. Usa setup_index() primero."
                
            # Ejecutar consulta
            query_engine = self.index.as_query_engine()
            response = query_engine.query(prompt)
            
            # Formatear respuesta según el formato solicitado
            if format_type == "markdown":
                return f"## Respuesta de LlamaIndex\n\n{response.response}"
            else:
                return response.response
                
        except Exception as e:
            error_msg = f"Error al ejecutar consulta LlamaIndex: {str(e)}"
            self.logger.error(error_msg)
            return f"ERROR: {error_msg}"
            
    def shutdown(self) -> bool:
        """
        Finaliza el plugin y libera recursos.
        
        Returns:
            bool: True si la finalización fue exitosa
        """
        self.logger.info("Cerrando LlamaIndex Plugin")
        self.index = None
        return True