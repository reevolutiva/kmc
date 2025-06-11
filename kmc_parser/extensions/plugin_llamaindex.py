"""
API Plugin - Plugin de ejemplo para KMC Parser que integra APIs externas
"""
from typing import Dict, Any, Optional
from ..handlers.base import GenerativeHandler
from ..core.registry import registry
from .lib.llamaindex import LlamaIndexMiddleware
from src.kmc.kmc_parser import (
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

@generative_handler("ai:llamaindex")
class LlamaIndexQuery(GenerativeHandler):
    """
    Handler para generar eventos de calendario.
    
    Este handler procesa variables como {{tool:calendar:eventos}}
    """
    __kmc_handler_type__ = "generative"
    __kmc_var_type__ = "tool:llamaindex"
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Inicializa el handler con configuración opcional.
        
        Args:
            config: Configuración específica para el handler
        """
        super().__init__(config)
        print("Inicializando LlamaIndex Query Handler...")
    
    def _generate_content(self, var):
        
        print("ejecutando _generate_content")
        prompt = var.prompt
        print(f"prompt: {prompt}")
        
        
        llamaindex_middleware = LlamaIndexMiddleware()
        # Procesar el prompt asociado a la variable
        print("Cargando LlamaIndex Middleware para la consulta...")
        if hasattr(var, 'prompt') and var.prompt:
            return llamaindex_middleware.llm_query(var.prompt)
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

