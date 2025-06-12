"""
API Plugin - Plugin de ejemplo para KMC Parser que integra APIs externas
"""
from typing import Dict, Any, Optional
from ..handlers.base import GenerativeHandler
from ..core.registry import registry
from .lib.llamaindex import LlamaIndexMiddleware
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

class LlamaIndexQuery(GenerativeHandler):
    """
    Handler para generar eventos de calendario.
    
    Este handler procesa variables como {{tool:calendar:eventos}}
    """
    __kmc_handler_type__ = "generative"
    __kmc_var_type__ = "tool:llamaindex"
    
    def _generate_content(self, var):
        llamaindex_middleware = LlamaIndexMiddleware()
        # Procesar el prompt asociado a la variable
        print("Cargando LlamaIndex Middleware para la consulta...")
        if hasattr(var, 'prompt') and var.prompt:
            return llamaindex_middleware.intelligent_query(var.prompt)
        return "Prompt no proporcionado"

class LlamaIndexGenerativeHandler(KMCPlugin):
    """
    Handler para integrar LlamaIndex con KMC Parser.
    
    Este handler procesará variables como {{llamaindex:query}} en documentos KMC.
    """
    __version__ = "0.1.0"
    
    def initialize(self):
        """Inicializa el plugin."""
        self.logger.info(f"Inicializando {self.name} v{self.version}")
        self.register_handlers()
        return True
    
    def register_handlers(self):
        """Registra los handlers proporcionados por este plugin."""
       
        toolLlamaindex = LlamaIndexQuery()
        registry.register_generative_handler("tool:llamaindex", toolLlamaindex )
        return 1

