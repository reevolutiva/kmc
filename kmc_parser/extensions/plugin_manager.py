"""
Plugin Manager - Gestor de plugins para KMC Parser
"""
import logging
import importlib
import pkgutil
import inspect
from typing import Dict, List, Any, Optional, Type, Set

from .plugin_base import KMCPlugin


class PluginManager:
    """
    Gestor de plugins para KMC Parser.
    
    Esta clase maneja la carga, inicialización y gestión del ciclo de vida
    de los plugins de extensión para KMC Parser, permitiendo extender las
    funcionalidades de forma modular.
    """
    
    def __init__(self):
        """Inicializa el gestor de plugins"""
        self.plugins: Dict[str, KMCPlugin] = {}
        self.logger = logging.getLogger("kmc.plugins")
    
    def register_plugin(self, plugin: KMCPlugin) -> bool:
        """
        Registra un plugin en el sistema.
        
        Args:
            plugin: Instancia del plugin a registrar
            
        Returns:
            True si el registro fue exitoso, False en caso contrario
        """
        if plugin.name in self.plugins:
            self.logger.warning(f"Plugin '{plugin.name}' ya está registrado. Omitiendo.")
            return False
        
        try:
            if plugin.initialize():
                self.plugins[plugin.name] = plugin
                plugin._registered = True
                self.logger.info(f"Plugin '{plugin.name}' v{plugin.version} registrado exitosamente")
                return True
            else:
                self.logger.warning(f"Plugin '{plugin.name}' falló al inicializarse")
                return False
        except Exception as e:
            self.logger.error(f"Error al registrar plugin '{plugin.name}': {str(e)}")
            return False
    
    def unregister_plugin(self, plugin_name: str) -> bool:
        """
        Elimina un plugin del sistema.
        
        Args:
            plugin_name: Nombre del plugin a eliminar
            
        Returns:
            True si se eliminó correctamente, False si no existía o hubo error
        """
        plugin = self.plugins.get(plugin_name)
        if not plugin:
            self.logger.warning(f"Plugin '{plugin_name}' no está registrado")
            return False
        
        try:
            plugin.cleanup()
            del self.plugins[plugin_name]
            plugin._registered = False
            self.logger.info(f"Plugin '{plugin_name}' eliminado exitosamente")
            return True
        except Exception as e:
            self.logger.error(f"Error al eliminar plugin '{plugin_name}': {str(e)}")
            return False
    
    def get_plugin(self, plugin_name: str) -> Optional[KMCPlugin]:
        """
        Obtiene un plugin por su nombre.
        
        Args:
            plugin_name: Nombre del plugin a obtener
            
        Returns:
            Instancia del plugin o None si no existe
        """
        return self.plugins.get(plugin_name)
    
    def get_all_plugins(self) -> List[KMCPlugin]:
        """
        Obtiene todos los plugins registrados.
        
        Returns:
            Lista de instancias de plugins
        """
        return list(self.plugins.values())
    
    def discover_plugins(self, package) -> List[Type[KMCPlugin]]:
        """
        Descubre automáticamente plugins disponibles en un paquete.
        
        Args:
            package: Paquete Python donde buscar plugins
            
        Returns:
            Lista de clases de plugins encontradas
        """
        discovered = []
        
        # Recorrer todos los módulos en el paquete
        for _, name, is_pkg in pkgutil.iter_modules(package.__path__):
            # Cargar el módulo
            module = importlib.import_module(f"{package.__name__}.{name}")
            
            # Buscar clases de plugin
            for item_name, item in inspect.getmembers(module, inspect.isclass):
                if (
                    issubclass(item, KMCPlugin) and 
                    item is not KMCPlugin and
                    not getattr(item, "__abstract__", False)
                ):
                    discovered.append(item)
                    self.logger.debug(f"Plugin descubierto: {item_name}")
        
        return discovered
    
    def load_discovered_plugins(self, package, configs: Optional[Dict[str, Dict[str, Any]]] = None) -> int:
        """
        Descubre y carga automáticamente plugins desde un paquete.
        
        Args:
            package: Paquete Python donde buscar plugins
            configs: Diccionario opcional con configuraciones para los plugins
                    (clave: nombre del plugin, valor: configuración)
            
        Returns:
            Número de plugins cargados exitosamente
        """
        discovered = self.discover_plugins(package)
        loaded_count = 0
        
        for plugin_cls in discovered:
            # Obtener configuración si existe
            config = None
            if configs and plugin_cls.__name__ in configs:
                config = configs[plugin_cls.__name__]
            
            # Instanciar y registrar el plugin
            try:
                plugin_instance = plugin_cls(config=config)
                if self.register_plugin(plugin_instance):
                    loaded_count += 1
            except Exception as e:
                self.logger.error(f"Error al cargar plugin {plugin_cls.__name__}: {str(e)}")
        
        return loaded_count
    
    def cleanup_all(self) -> None:
        """Limpia y elimina todos los plugins registrados"""
        for name in list(self.plugins.keys()):
            self.unregister_plugin(name)


# Instancia global del gestor de plugins
plugin_manager = PluginManager()