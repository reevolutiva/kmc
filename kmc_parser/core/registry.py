"""
Registry - Sistema central de registro para handlers y extensiones de KMC Parser
"""
from typing import Dict, Any, List, Optional, Callable, Type
import logging
import inspect

class HandlerRegistry:
    """
    Registro centralizado para handlers de variables KMC.
    
    Esta clase implementa un patrón Registry para mantener y gestionar
    handlers para diferentes tipos de variables (contexto, metadata, generativas).
    Permite el descubrimiento automático y el registro declarativo de handlers.
    """
    
    def __init__(self):
        """Inicializa los registros para cada tipo de variable"""
        self.context_handlers: Dict[str, Callable] = {}
        self.metadata_handlers: Dict[str, Callable] = {}
        self.generative_handlers: Dict[str, Callable] = {}
        self.logger = logging.getLogger("kmc.registry")
    
    def register_context_handler(self, var_type: str, handler: Callable) -> None:
        """
        Registra un handler para variables contextuales [[tipo:nombre]].
        
        Args:
            var_type: Tipo de variable contextual (ej. "project", "user", "org")
            handler: Función que procesa la variable y retorna un valor
        """
        self.logger.debug(f"Registrando handler de contexto para '{var_type}'")
        self.context_handlers[var_type] = handler
    
    def register_metadata_handler(self, var_type: str, handler: Callable) -> None:
        """
        Registra un handler para variables de metadata [{tipo:nombre}].
        
        Args:
            var_type: Tipo de variable metadata (ej. "doc", "kb")
            handler: Función que procesa la variable y retorna un valor
        """
        self.logger.debug(f"Registrando handler de metadata para '{var_type}'")
        self.metadata_handlers[var_type] = handler
    
    def register_generative_handler(self, var_type: str, handler: Callable) -> None:
        """
        Registra un handler para variables generativas {{categoria:subtipo:nombre}}.
        
        Args:
            var_type: Tipo de variable generativa (ej. "ai:gpt4", "api:weather")
            handler: Función que procesa la variable generativa y retorna un valor
        """
        self.logger.debug(f"Registrando handler generativo para '{var_type}'")
        self.generative_handlers[var_type] = handler
    
    def get_context_handler(self, var_type: str) -> Optional[Callable]:
        """Obtiene el handler registrado para un tipo de variable contextual"""
        return self.context_handlers.get(var_type)
    
    def get_metadata_handler(self, var_type: str) -> Optional[Callable]:
        """Obtiene el handler registrado para un tipo de variable de metadata"""
        return self.metadata_handlers.get(var_type)
    
    def get_generative_handler(self, var_type: str) -> Optional[Callable]:
        """Obtiene el handler registrado para un tipo de variable generativa"""
        return self.generative_handlers.get(var_type)
    
    def register_handlers_from_module(self, module) -> int:
        """
        Registra automáticamente todos los handlers definidos en un módulo.
        Los handlers deben tener un atributo `__kmc_handler_type__` y `__kmc_var_type__`.
        
        Args:
            module: Módulo Python desde donde cargar los handlers
            
        Returns:
            Número de handlers registrados
        """
        count = 0
        
        # Buscar todas las clases o funciones en el módulo
        for name, obj in inspect.getmembers(module):
            # Verificar si el objeto tiene los atributos necesarios
            if hasattr(obj, "__kmc_handler_type__") and hasattr(obj, "__kmc_var_type__"):
                handler_type = getattr(obj, "__kmc_handler_type__")
                var_type = getattr(obj, "__kmc_var_type__")
                
                # Registrar el handler según su tipo
                if handler_type == "context":
                    self.register_context_handler(var_type, obj())
                elif handler_type == "metadata":
                    self.register_metadata_handler(var_type, obj())
                elif handler_type == "generative":
                    self.register_generative_handler(var_type, obj())
                
                count += 1
        
        return count
    
    def register_from_config(self, config: Dict[str, Any]) -> int:
        """
        Registra handlers a partir de una configuración en diccionario.
        
        Args:
            config: Configuración con handlers para cada tipo de variable
            
        Returns:
            Número de handlers registrados
        """
        count = 0
        
        # Registrar handlers de contexto
        for var_type, handler in config.get("context", {}).items():
            self.register_context_handler(var_type, handler)
            count += 1
        
        # Registrar handlers de metadata
        for var_type, handler in config.get("metadata", {}).items():
            self.register_metadata_handler(var_type, handler)
            count += 1
        
        # Registrar handlers generativos
        for var_type, handler in config.get("generative", {}).items():
            self.register_generative_handler(var_type, handler)
            count += 1
        
        return count


# Instancia global del registro
registry = HandlerRegistry()