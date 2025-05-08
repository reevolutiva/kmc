"""
Tests para la funcionalidad de autodetección de extensiones del KMC Parser.
"""
import unittest
import tempfile
import os
import shutil
import logging

# Cambiar importaciones relativas por absolutas
from kmc_parser.extensions.auto_discovery import ExtensionDiscovery
from kmc_parser.parser import KMCParser
from kmc_parser.core import registry
from kmc_parser.extensions.plugin_base import KMCPlugin

# Configurar logging para pruebas
logging.basicConfig(level=logging.INFO)


class TestAutoDiscovery(unittest.TestCase):
    """Pruebas para la autodetección de extensiones."""

    def setUp(self):
        """Configuración inicial para cada prueba."""
        # Crear un directorio temporal para las pruebas
        self.test_dir = tempfile.mkdtemp()
        
        # Crear directorios de extensión dentro del directorio temporal
        self.extensions_dir = os.path.join(self.test_dir, "extensions")
        self.user_extensions_dir = os.path.join(self.test_dir, "user_extensions")
        self.custom_handlers_dir = os.path.join(self.test_dir, "custom_handlers")
        self.plugins_dir = os.path.join(self.test_dir, "plugins")
        
        os.makedirs(self.extensions_dir, exist_ok=True)
        os.makedirs(self.user_extensions_dir, exist_ok=True)
        os.makedirs(self.custom_handlers_dir, exist_ok=True)
        os.makedirs(self.plugins_dir, exist_ok=True)
        
        # Crear archivos __init__.py en cada directorio para que Python los reconozca como paquetes
        self._create_init_file(self.extensions_dir)
        self._create_init_file(self.user_extensions_dir)
        self._create_init_file(self.custom_handlers_dir)
        self._create_init_file(self.plugins_dir)
        
        # Resetear el registro para cada prueba
        registry.clear_all()
        
        # Instancia de descubrimiento para pruebas
        self.discovery = ExtensionDiscovery()

    def tearDown(self):
        """Limpieza después de cada prueba."""
        # Eliminar el directorio temporal y todos sus archivos
        shutil.rmtree(self.test_dir)
        
        # Resetear el registro nuevamente
        registry.clear_all()

    def _create_init_file(self, directory):
        """Crea un archivo __init__.py en el directorio especificado."""
        init_file = os.path.join(directory, "__init__.py")
        with open(init_file, 'w') as f:
            f.write("# Este archivo permite que Python trate este directorio como un paquete")
        return init_file

    def _create_context_handler_file(self, dir_path, handler_name, handler_type):
        """Crea un archivo con un handler contextual de prueba."""
        handler_code = f'''
from kmc_parser.handlers.base import ContextHandler, context_handler

@context_handler("{handler_type}")
class {handler_name}(ContextHandler):
    """Handler de prueba para variables contextuales [[{handler_type}:nombre]]."""
    
    def _get_context_value(self, var_name):
        return f"Valor de prueba: {handler_type}:{{{{var_name}}}}"
'''
        file_path = os.path.join(dir_path, f"{handler_name.lower()}.py")
        with open(file_path, 'w') as f:
            f.write(handler_code)
        return file_path

    def _create_metadata_handler_file(self, dir_path, handler_name, handler_type):
        """Crea un archivo con un handler de metadata de prueba."""
        handler_code = f'''
from kmc_parser.handlers.base import MetadataHandler, metadata_handler

@metadata_handler("{handler_type}")
class {handler_name}(MetadataHandler):
    """Handler de prueba para variables de metadata [{{{handler_type}:nombre}}]."""
    
    def _get_metadata_value(self, var_name):
        return f"Valor de prueba: {handler_type}:{{{{var_name}}}}"
'''
        file_path = os.path.join(dir_path, f"{handler_name.lower()}.py")
        with open(file_path, 'w') as f:
            f.write(handler_code)
        return file_path

    def _create_generative_handler_file(self, dir_path, handler_name, category, subtype):
        """Crea un archivo con un handler generativo de prueba."""
        handler_code = f'''
from kmc_parser.handlers.base import GenerativeHandler, generative_handler

@generative_handler("{category}:{subtype}")
class {handler_name}(GenerativeHandler):
    """Handler de prueba para variables generativas {{{{{category}:{subtype}:nombre}}}}."""
    
    def _generate_content(self, var):
        return f"Contenido generado para {{{{var.category}}}}:{{{{var.subtype}}}}:{{{{var.name}}}}"
'''
        file_path = os.path.join(dir_path, f"{handler_name.lower()}.py")
        with open(file_path, 'w') as f:
            f.write(handler_code)
        return file_path

    def _create_plugin_file(self, dir_path, plugin_name):
        """Crea un archivo con un plugin de prueba."""
        plugin_code = f'''
from kmc_parser.extensions.plugin_base import KMCPlugin
from kmc_parser.core import registry

class {plugin_name}(KMCPlugin):
    """Plugin de prueba para KMC."""
    
    def initialize(self):
        """Método de inicialización requerido por KMCPlugin."""
        self.logger.info("{plugin_name} inicializado")
        # Registrar un handler contextual desde el plugin
        registry.register_context_handler("plugin_test", 
            lambda var_name: f"Valor del plugin: {{{{var_name}}}}")
        return True
'''
        file_path = os.path.join(dir_path, f"{plugin_name.lower()}.py")
        with open(file_path, 'w') as f:
            f.write(plugin_code)
        return file_path

    def _create_invalid_file(self, dir_path, file_name):
        """Crea un archivo Python inválido para pruebas de robustez."""
        file_path = os.path.join(dir_path, f"{file_name}.py")
        with open(file_path, 'w') as f:
            f.write("This is not valid Python code def )(")
        return file_path

    def test_discover_context_handlers(self):
        """Prueba la detección de handlers contextuales."""
        # Crear un handler contextual en cada directorio de extensiones
        self._create_context_handler_file(self.extensions_dir, "TestExtHandler", "test_ext")
        self._create_context_handler_file(self.user_extensions_dir, "TestUserHandler", "test_user")
        
        # Ejecutar descubrimiento
        self.discovery.discover_all_extensions(base_path=self.test_dir)
        
        # Verificar que los handlers fueron descubiertos
        self.assertIn("test_ext", registry.context_handlers)
        self.assertIn("test_user", registry.context_handlers)
        
    def test_discover_metadata_handlers(self):
        """Prueba la detección de handlers de metadata."""
        # Crear un handler de metadata
        self._create_metadata_handler_file(self.custom_handlers_dir, "TestMetaHandler", "test_meta")
        
        # Ejecutar descubrimiento
        self.discovery.discover_all_extensions(base_path=self.test_dir)
        
        # Verificar que el handler fue descubierto
        self.assertIn("test_meta", registry.metadata_handlers)

    def test_discover_generative_handlers(self):
        """Prueba la detección de handlers generativos."""
        # Crear un handler generativo
        self._create_generative_handler_file(
            self.custom_handlers_dir, "TestGenHandler", "test", "gen")
        
        # Ejecutar descubrimiento
        self.discovery.discover_all_extensions(base_path=self.test_dir)
        
        # Verificar que el handler fue descubierto
        self.assertIn("test:gen", registry.generative_handlers)

    def test_discover_plugins(self):
        """Prueba la detección de plugins."""
        # Crear un plugin
        self._create_plugin_file(self.plugins_dir, "TestPlugin")
        
        # Ejecutar descubrimiento
        stats = self.discovery.discover_all_extensions(base_path=self.test_dir)
        
        # Verificar que al menos un plugin fue descubierto
        self.assertGreaterEqual(stats["plugins"], 1, "No se detectó ningún plugin")
        self.assertGreaterEqual(len(registry.plugins), 1, "No se registró ningún plugin")

    def test_parser_with_autodiscovery(self):
        """Prueba la autodetección al inicializar KMCParser."""
        # Crear extensiones para la prueba
        self._create_context_handler_file(self.extensions_dir, "ParserTestHandler", "parser_test")
        self._create_plugin_file(self.plugins_dir, "ParserTestPlugin")
        
        # Crear un parser con autodetección habilitada
        parser = KMCParser(auto_discover=True, ext_directory=self.test_dir)
        
        # Verificar que los handlers detectados se registraron en el parser
        self.assertIn("parser_test", registry.context_handlers)
        self.assertIn("plugin_test", registry.context_handlers)
        
        # Crear un documento simple que usa los handlers autodescubiertos
        # Agregar definiciones KMC_DEFINITION para variables de metadata y generativas
        content = """
# Prueba Autodetección
[[parser_test:hello]]
[[plugin_test:world]]

<!-- KMC_DEFINITION FOR [{test_meta:sample}]:
GENERATIVE_SOURCE = {{test:gen:sample}}
PROMPT = "Un prompt de prueba"
FORMAT = "text"
-->

[{test_meta:sample}]
"""
        
        # Renderizar el documento
        resultado = parser.render(content)
        
        # Verificar que las variables contextuales se resolvieron correctamente
        self.assertIn("Valor de prueba: parser_test:hello", resultado)
        self.assertIn("Valor del plugin: world", resultado)

    def test_parser_without_autodiscovery(self):
        """Prueba deshabilitar la autodetección en KMCParser."""
        # Crear extensiones para la prueba
        self._create_context_handler_file(self.extensions_dir, "NoAutoHandler", "no_auto")
        
        # Crear un parser con autodetección deshabilitada
        parser = KMCParser(auto_discover=False, ext_directory=self.test_dir)
        
        # Crear un documento simple con las variables que usan los handlers
        content = """
# Prueba Sin Autodetección
[[no_auto:test]]
"""
        
        # Renderizar el documento sin registrar handlers
        resultado = parser.render(content)
        
        # Las variables no deben resolverse ya que no hay handler registrado
        self.assertIn("[[no_auto:test]]", resultado)

    def test_error_handling(self):
        """Prueba el manejo de errores en archivos inválidos."""
        # Crear un archivo Python sintácticamente inválido
        self._create_invalid_file(self.extensions_dir, "invalid_handler")
        
        # Ejecutar descubrimiento, debería manejar el error sin fallar
        try:
            self.discovery.discover_all_extensions(base_path=self.test_dir)
            # Si llegamos aquí, el manejo de errores funciona
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"La autodetección no manejó correctamente los errores: {str(e)}")

    def test_multiple_directories(self):
        """Prueba la detección en múltiples directorios de extensiones."""
        # Crear handlers en diferentes directorios
        self._create_context_handler_file(self.extensions_dir, "HandlerInExt", "ext_dir")
        self._create_metadata_handler_file(self.user_extensions_dir, "HandlerInUser", "user_dir")
        self._create_generative_handler_file(self.custom_handlers_dir, "HandlerInCustom", "custom", "dir")
        self._create_plugin_file(self.plugins_dir, "PluginInPlugins")
        
        # Ejecutar descubrimiento
        self.discovery.discover_all_extensions(base_path=self.test_dir)
        
        # Verificar que se encontraron handlers en cada directorio
        self.assertIn("ext_dir", registry.context_handlers)
        self.assertIn("user_dir", registry.metadata_handlers)
        self.assertIn("custom:dir", registry.generative_handlers)
        self.assertGreaterEqual(len(registry.plugins), 1)


if __name__ == '__main__':
    unittest.main()