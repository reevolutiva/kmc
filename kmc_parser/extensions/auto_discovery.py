"""
Módulo de autodetección de extensiones para KMC Parser.

Este módulo proporciona la funcionalidad para descubrir automáticamente 
extensiones (handlers y plugins) sin necesidad de registro manual.
"""
import os
import logging
import importlib.util
import sys
import traceback
import inspect

# Corregir importaciones relativas por absolutas
from kmc_parser.core import registry
from kmc_parser.extensions.plugin_base import KMCPlugin

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
        # Caché de módulos ya procesados para evitar re-escaneo
        self._processed_modules = set()

    def discover_all_extensions(self, base_path=None, custom_dirs=None):
        """
        Descubre todas las extensiones disponibles en los directorios estándar y personalizados

        Args:
            base_path: Ruta base donde buscar los directorios de extensiones
                       (por defecto es la raíz del paquete KMC)
            custom_dirs: Lista de directorios personalizados adicionales para buscar extensiones

        Returns:
            Diccionario con estadísticas de los elementos descubiertos
        """
        base_path = base_path or os.getcwd()
        self.logger.info(f"Iniciando descubrimiento de extensiones desde: {base_path}")
        
        stats = {"handlers": 0, "plugins": 0}
        
        # Escanear directorios estándar
        for directory in self.EXTENSION_DIRECTORIES:
            full_path = os.path.join(base_path, directory)
            if os.path.exists(full_path):
                self.logger.debug(f"Escaneando directorio estándar: {full_path}")
                try:
                    h_count = self._scan_directory_for_handlers(full_path)
                    p_count = self._scan_directory_for_plugins(full_path)
                    stats["handlers"] += h_count
                    stats["plugins"] += p_count
                    self.logger.info(f"Encontrados en {directory}: {h_count} handlers, {p_count} plugins")
                except Exception as e:
                    self.logger.error(f"Error al escanear directorio {full_path}: {str(e)}")
                    self.logger.debug(traceback.format_exc())
            else:
                self.logger.debug(f"Directorio {full_path} no existe, omitiendo")

        # Escanear directorios personalizados si se proporcionan
        if custom_dirs:
            for directory in custom_dirs:
                if os.path.isabs(directory):
                    full_path = directory
                else:
                    full_path = os.path.join(base_path, directory)
                
                if os.path.exists(full_path):
                    self.logger.debug(f"Escaneando directorio personalizado: {full_path}")
                    try:
                        h_count = self._scan_directory_for_handlers(full_path)
                        p_count = self._scan_directory_for_plugins(full_path)
                        stats["handlers"] += h_count
                        stats["plugins"] += p_count
                        self.logger.info(f"Encontrados en {directory}: {h_count} handlers, {p_count} plugins")
                    except Exception as e:
                        self.logger.error(f"Error al escanear directorio personalizado {full_path}: {str(e)}")
                        self.logger.debug(traceback.format_exc())
                else:
                    self.logger.warning(f"Directorio personalizado {full_path} no existe")

        self.logger.info(f"Descubrimiento completado. Totales: {stats['handlers']} handlers, {stats['plugins']} plugins")
        return stats

    def _scan_directory_for_handlers(self, directory):
        """Busca y registra handlers en un directorio"""
        self.logger.info(f"Escaneando handlers en: {directory}")
        handlers_count = 0

        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(".py") and file != "__init__.py":
                    module_name = os.path.splitext(file)[0]
                    module_path = os.path.join(root, file)
                    
                    # Evitar procesar el mismo módulo más de una vez
                    if module_path in self._processed_modules:
                        self.logger.debug(f"Módulo ya procesado, omitiendo: {module_path}")
                        continue
                    
                    self._processed_modules.add(module_path)
                    
                    try:
                        spec = importlib.util.spec_from_file_location(module_name, module_path)
                        if spec is None:
                            self.logger.warning(f"No se pudo cargar especificación para: {module_path}")
                            continue
                            
                        module = importlib.util.module_from_spec(spec)
                        
                        # Capturar salidas y excepciones durante la ejecución del módulo
                        try:
                            spec.loader.exec_module(module)
                        except Exception as e:
                            self.logger.error(f"Error al ejecutar módulo {module_path}: {str(e)}")
                            self.logger.debug(traceback.format_exc())
                            continue

                        # Buscar handlers en el módulo
                        for name, obj in vars(module).items():
                            try:
                                if hasattr(obj, "__kmc_handler_type__") and hasattr(obj, "__kmc_var_type__"):
                                    handler_type = getattr(obj, "__kmc_handler_type__")
                                    var_type = getattr(obj, "__kmc_var_type__")
                                    
                                    # Validar el tipo de handler
                                    if handler_type in ["context", "metadata", "generative"]:
                                        self.discovered_handlers.add((handler_type, var_type))
                                        handlers_count += 1
                                        self.logger.debug(f"Handler descubierto: {handler_type}:{var_type} en {module_path}")
                            except Exception as e:
                                self.logger.error(f"Error al procesar objeto {name} en {module_path}: {str(e)}")
                                
                    except Exception as e:
                        self.logger.error(f"Error al cargar módulo {module_path}: {str(e)}")
                        self.logger.debug(traceback.format_exc())

        return handlers_count

    def _scan_directory_for_plugins(self, directory):
        """Busca y registra plugins en un directorio"""
        self.logger.info(f"Escaneando plugins en: {directory}")
        plugins_count = 0

        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(".py") and file != "__init__.py":
                    module_name = os.path.splitext(file)[0]
                    module_path = os.path.join(root, file)
                    
                    # Evitar procesar el mismo módulo más de una vez
                    if module_path in self._processed_modules:
                        self.logger.debug(f"Módulo ya procesado, omitiendo: {module_path}")
                        continue
                        
                    self._processed_modules.add(module_path)
                    
                    try:
                        spec = importlib.util.spec_from_file_location(module_name, module_path)
                        if spec is None:
                            self.logger.warning(f"No se pudo cargar especificación para: {module_path}")
                            continue
                            
                        module = importlib.util.module_from_spec(spec)
                        
                        try:
                            spec.loader.exec_module(module)
                        except Exception as e:
                            self.logger.error(f"Error al ejecutar módulo {module_path}: {str(e)}")
                            self.logger.debug(traceback.format_exc())
                            continue

                        # Buscar plugins en el módulo (clases que heredan de KMCPlugin)
                        for name, obj in vars(module).items():
                            try:
                                if inspect.isclass(obj) and issubclass(obj, KMCPlugin) and obj != KMCPlugin:
                                    # Crear instancia del plugin
                                    plugin_instance = obj()
                                    # Registrar el plugin
                                    if registry.register_plugin(plugin_instance):
                                        self.discovered_plugins.add(plugin_instance)
                                        plugins_count += 1
                                        self.logger.debug(f"Plugin descubierto y registrado: {name} en {module_path}")
                            except (TypeError, Exception) as e:
                                # TypeError ocurre en issubclass si obj no es una clase
                                if isinstance(e, TypeError):
                                    continue
                                self.logger.error(f"Error al procesar clase {name} en {module_path}: {str(e)}")
                    
                    except Exception as e:
                        self.logger.error(f"Error al cargar módulo {module_path}: {str(e)}")
                        self.logger.debug(traceback.format_exc())

        return plugins_count
        
    def clear_cache(self):
        """Limpia la caché de módulos procesados para forzar un re-escaneo completo"""
        self._processed_modules.clear()
        self.logger.info("Caché de módulos procesados limpiada")
