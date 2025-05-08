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
        handlers_count = 0

        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(".py"):
                    module_name = os.path.splitext(file)[0]
                    module_path = os.path.join(root, file)
                    spec = importlib.util.spec_from_file_location(module_name, module_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    for name, obj in vars(module).items():
                        if hasattr(obj, "__kmc_handler_type__") and hasattr(obj, "__kmc_var_type__"):
                            handler_type = getattr(obj, "__kmc_handler_type__")
                            var_type = getattr(obj, "__kmc_var_type__")

                            if handler_type == "context":
                                self.discovered_handlers.add((handler_type, var_type))
                            elif handler_type == "metadata":
                                self.discovered_handlers.add((handler_type, var_type))
                            elif handler_type == "generative":
                                self.discovered_handlers.add((handler_type, var_type))

                            handlers_count += 1

        return handlers_count

    def _scan_directory_for_plugins(self, directory):
        """Busca y registra plugins en un directorio"""
        self.logger.info(f"Escaneando plugins en: {directory}")
        plugins_count = 0

        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(".py"):
                    module_name = os.path.splitext(file)[0]
                    module_path = os.path.join(root, file)
                    spec = importlib.util.spec_from_file_location(module_name, module_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    for name, obj in vars(module).items():
                        if hasattr(obj, "__bases__") and "KMCPlugin" in [base.__name__ for base in obj.__bases__]:
                            self.discovered_plugins.add(obj)
                            plugins_count += 1

        return plugins_count
