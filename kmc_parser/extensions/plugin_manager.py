"""
Gestor de plugins para KMC Parser.

Este módulo proporciona un gestor centralizado para los plugins de KMC,
facilitando su registro, configuración y utilización.
"""
import logging
import importlib
import pkgutil  # Añadir importación faltante
from typing import Dict, List, Any, Optional

from .plugin_base import KMCPlugin
from ..core import registry

class PluginManager:
    """
    Gestor centralizado para plugins de KMC.
    
    Proporciona métodos para cargar, configurar y acceder a plugins registrados.
    """
    
    def __init__(self):
        """Inicializa el gestor de plugins."""
        self.logger = logging.getLogger("kmc.plugin_manager")
        # Mantener un registro de los plugins cargados y sus opciones
        self.plugins_config: Dict[str, Dict[str, Any]] = {}
    
    def load_plugin(self, plugin_class_or_module: Any, options: Dict[str, Any] = None) -> bool:
        """
        Carga e inicializa un plugin específico.
        
        Args:
            plugin_class_or_module: Clase del plugin o ruta al módulo del plugin
            options: Opciones de configuración para el plugin
            
        Returns:
            bool: True si el plugin se cargó correctamente
        """
        options = options or {}
        
        # Determinar si lo que recibimos es una clase o una ruta de módulo
        if isinstance(plugin_class_or_module, str):
            # Es una ruta de módulo, intentar importarla
            try:
                module = importlib.import_module(plugin_class_or_module)
                # Buscar todas las clases en el módulo que heredan de KMCPlugin
                plugin_classes = []
                for name in dir(module):
                    obj = getattr(module, name)
                    if isinstance(obj, type) and issubclass(obj, KMCPlugin) and obj != KMCPlugin:
                        plugin_classes.append(obj)
                
                if not plugin_classes:
                    self.logger.error(f"No se encontraron plugins en el módulo {plugin_class_or_module}")
                    return False
                
                # Inicializar todos los plugins encontrados
                for plugin_class in plugin_classes:
                    try:
                        plugin = plugin_class()
                        if registry.register_plugin(plugin):
                            self.plugins_config[plugin.__class__.__name__] = options
                    except Exception as e:
                        self.logger.error(f"Error al inicializar plugin {plugin_class.__name__}: {str(e)}")
                        return False
                
                return True
                
            except ImportError as e:
                self.logger.error(f"No se pudo importar el módulo del plugin {plugin_class_or_module}: {str(e)}")
                return False
                
        elif isinstance(plugin_class_or_module, type) and issubclass(plugin_class_or_module, KMCPlugin):
            # Es una clase de plugin, inicializarla directamente
            try:
                plugin = plugin_class_or_module()
                if registry.register_plugin(plugin):
                    self.plugins_config[plugin.__class__.__name__] = options
                    return True
                return False
            except Exception as e:
                self.logger.error(f"Error al inicializar plugin {plugin_class_or_module.__name__}: {str(e)}")
                return False
                
        else:
            self.logger.error(f"Tipo de entrada inválido para cargar plugin: {type(plugin_class_or_module)}")
            return False
    
    def get_plugin_config(self, plugin_name: str) -> Dict[str, Any]:
        """
        Obtiene la configuración actual de un plugin específico.
        
        Args:
            plugin_name: Nombre de la clase del plugin
            
        Returns:
            Dict: Opciones de configuración del plugin o diccionario vacío si no existe
        """
        return self.plugins_config.get(plugin_name, {})
    
    def update_plugin_config(self, plugin_name: str, options: Dict[str, Any]) -> bool:
        """
        Actualiza la configuración de un plugin específico.
        
        Args:
            plugin_name: Nombre de la clase del plugin
            options: Nuevas opciones de configuración (se fusionarán con las existentes)
            
        Returns:
            bool: True si la actualización fue exitosa
        """
        if plugin_name not in self.plugins_config:
            self.logger.warning(f"Intentando actualizar configuración de plugin no registrado: {plugin_name}")
            self.plugins_config[plugin_name] = {}
        
        # Fusionar opciones nuevas con existentes
        self.plugins_config[plugin_name].update(options)
        self.logger.debug(f"Configuración actualizada para plugin {plugin_name}")
        return True
    
    def get_plugin_instance(self, plugin_name: str) -> Optional[KMCPlugin]:
        """
        Obtiene la instancia de un plugin registrado por su nombre.
        
        Args:
            plugin_name: Nombre de la clase del plugin
            
        Returns:
            KMCPlugin: Instancia del plugin o None si no se encuentra
        """
        # Buscar entre los plugins registrados en registry
        for plugin in registry.plugins:
            if plugin.__class__.__name__ == plugin_name:
                return plugin
        return None
    
    def load_discovered_plugins(self, module_or_package):
        """
        Carga plugins descubiertos en un módulo o paquete específico.
        
        Esta función es útil para cargar plugins que se descubren durante
        la importación de un módulo o paquete.
        
        Args:
            module_or_package: Módulo o paquete donde buscar plugins
            
        Returns:
            int: Número de plugins cargados correctamente
        """
        loaded_count = 0
        
        if hasattr(module_or_package, "__path__"):
            # Es un paquete, intentar importar todos sus submódulos
            package_name = module_or_package.__name__
            try:
                # Importar todos los submódulos encontrados
                for _, name, is_pkg in pkgutil.iter_modules(module_or_package.__path__, f"{package_name}."):
                    if not is_pkg:
                        try:
                            importlib.import_module(name)
                            loaded_count += 1
                        except ImportError:
                            self.logger.warning(f"No se pudo importar el módulo {name}")
            except Exception as e:
                self.logger.error(f"Error al cargar plugins del paquete {package_name}: {str(e)}")
                
        return loaded_count


# Instancia global del gestor de plugins
plugin_manager = PluginManager()