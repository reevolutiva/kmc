"""
Registro central para KMC.

Este módulo proporciona un registro centralizado para handlers de variables y plugins.
"""
import logging
from typing import Dict, Any, List, Optional, Callable, Union

logger = logging.getLogger("kmc.registry")

class HandlerRegistry:
    """Registro centralizado para handlers de variables y plugins de KMC."""
    
    def __init__(self):
        """Inicializa un nuevo registro vacío."""
        self.context_handlers: Dict[str, Callable] = {}
        self.metadata_handlers: Dict[str, Callable] = {}
        self.generative_handlers: Dict[str, Callable] = {}
        self.plugins: List[Any] = []
        self.logger = logger
    
    def register_context_handler(self, var_type: str, handler_function: Callable) -> None:
        """
        Registra un handler para variables contextuales.
        
        Args:
            var_type: Tipo de variable (ej. "project", "user")
            handler_function: Función para resolver variables
        """
        self.logger.debug(f"Registrando handler contextual para: {var_type}")
        self.context_handlers[var_type] = handler_function
    
    def register_metadata_handler(self, var_type: str, handler_function: Callable) -> None:
        """
        Registra un handler para variables de metadata.
        
        Args:
            var_type: Tipo de variable (ej. "doc", "kb")
            handler_function: Función para resolver variables
        """
        self.logger.debug(f"Registrando handler de metadata para: {var_type}")
        self.metadata_handlers[var_type] = handler_function
    
    def register_generative_handler(self, var_type: str, handler_function: Callable) -> None:
        """
        Registra un handler para variables generativas.
        
        Args:
            var_type: Tipo de variable (ej. "ai:gpt4", "tool:sentiment")
            handler_function: Función para generar contenido
        """
        self.logger.debug(f"Registrando handler generativo para: {var_type}")
        self.generative_handlers[var_type] = handler_function
    
    def register_plugin(self, plugin_instance: Any) -> bool:
        """
        Registra e inicializa un plugin KMC.
        
        Args:
            plugin_instance: Instancia del plugin a registrar
            
        Returns:
            bool: True si el plugin se registró e inicializó correctamente
        """
        plugin_name = plugin_instance.__class__.__name__
        self.logger.debug(f"Registrando plugin: {plugin_name}")
        
        # Verificar que el plugin no esté ya registrado
        for existing_plugin in self.plugins:
            if existing_plugin.__class__.__name__ == plugin_name:
                self.logger.warning(f"Plugin {plugin_name} ya está registrado, omitiendo")
                return False
        
        # Inicializar el plugin
        try:
            if plugin_instance.initialize():
                self.plugins.append(plugin_instance)
                self.logger.info(f"Plugin {plugin_name} registrado e inicializado correctamente")
                return True
            else:
                self.logger.error(f"Plugin {plugin_name} falló en inicialización")
                return False
        except Exception as e:
            self.logger.error(f"Error al inicializar plugin {plugin_name}: {str(e)}")
            return False
    
    # Métodos de acceso para obtener handlers registrados
    def get_context_handler(self, var_type: str) -> Optional[Callable]:
        """
        Obtiene un handler contextual por su tipo.
        
        Args:
            var_type: Tipo de variable contextual
            
        Returns:
            Callable o None si no se encuentra el handler
        """
        return self.context_handlers.get(var_type)
    
    def get_metadata_handler(self, var_type: str) -> Optional[Callable]:
        """
        Obtiene un handler de metadata por su tipo.
        
        Args:
            var_type: Tipo de variable de metadata
            
        Returns:
            Callable o None si no se encuentra el handler
        """
        return self.metadata_handlers.get(var_type)
    
    def get_generative_handler(self, var_type: str) -> Optional[Callable]:
        """
        Obtiene un handler generativo por su tipo.
        
        Args:
            var_type: Tipo de variable generativa
            
        Returns:
            Callable o None si no se encuentra el handler
        """
        return self.generative_handlers.get(var_type)
    
    def clear_handlers(self) -> None:
        """Limpia todos los handlers registrados."""
        self.context_handlers = {}
        self.metadata_handlers = {}
        self.generative_handlers = {}
        self.logger.debug("Todos los handlers han sido eliminados del registro")
    
    def clear_plugins(self) -> None:
        """Limpia y finaliza todos los plugins registrados."""
        for plugin in self.plugins:
            try:
                plugin.shutdown()
            except Exception as e:
                self.logger.error(f"Error al cerrar plugin {plugin.__class__.__name__}: {str(e)}")
        
        self.plugins = []
        self.logger.debug("Todos los plugins han sido eliminados del registro")
    
    def clear_all(self) -> None:
        """Limpia todos los handlers y plugins registrados."""
        self.clear_handlers()
        self.clear_plugins()
        self.logger.debug("Registro completamente limpio")

# Instancia global del registro para acceso fácil
registry = HandlerRegistry()