import os
import logging
import importlib.util

class ExtensionDiscovery:
    """Descubre y carga automáticamente extensiones del SDK KMC"""

    EXTENSION_DIRECTORIES = [
        "extensions",        # Extensiones propias del SDK
        "user_extensions",   # Extensiones creadas por el usuario
        "custom_handlers",   # Handlers personalizados
        "plugins"            # Plugins adicionales
    ]

    def __init__(self):
        """Inicializa el sistema de descubrimiento"""
        self.logger = logging.getLogger("kmc.auto_discovery")
        self.discovered_handlers = set()
        self.discovered_plugins = set()

    def discover_all_extensions(self, base_path=None):
        """
        Descubre todas las extensiones disponibles en los directorios estándar

        Args:
            base_path: Ruta base donde buscar los directorios de extensiones
                       (por defecto es la raíz del paquete KMC)

        Returns:
            Diccionario con estadísticas de los elementos descubiertos
        """
        base_path = base_path or os.getcwd()
        stats = {"handlers": 0, "plugins": 0}

        for directory in self.EXTENSION_DIRECTORIES:
            full_path = os.path.join(base_path, directory)
            if os.path.exists(full_path):
                stats["handlers"] += self._scan_directory_for_handlers(full_path)
                stats["plugins"] += self._scan_directory_for_plugins(full_path)

        return stats

    def _scan_directory_for_handlers(self, directory):
        """Busca y registra handlers en un directorio"""
        self.logger.info(f"Escaneando handlers en: {directory}")
        handler_count = 0

        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(".py"):
                    module_name = os.path.splitext(file)[0]
                    module_path = os.path.join(root, file)
                    spec = importlib.util.spec_from_file_location(module_name, module_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if hasattr(attr, "__kmc_handler_type__") and hasattr(attr, "__kmc_var_type__"):
                            handler_type = getattr(attr, "__kmc_handler_type__")
                            var_type = getattr(attr, "__kmc_var_type__")

                            if handler_type == "context":
                                self.discovered_handlers.add((handler_type, var_type, attr))
                            elif handler_type == "metadata":
                                self.discovered_handlers.add((handler_type, var_type, attr))
                            elif handler_type == "generative":
                                self.discovered_handlers.add((handler_type, var_type, attr))

                            handler_count += 1

        return handler_count

    def _scan_directory_for_plugins(self, directory):
        """Busca y registra plugins en un directorio"""
        self.logger.info(f"Escaneando plugins en: {directory}")
        plugin_count = 0

        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(".py"):
                    module_name = os.path.splitext(file)[0]
                    module_path = os.path.join(root, file)
                    spec = importlib.util.spec_from_file_location(module_name, module_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if isinstance(attr, type) and issubclass(attr, KMCPlugin) and attr is not KMCPlugin:
                            self.discovered_plugins.add(attr)
                            plugin_count += 1

        return plugin_count
