"""
Tests para el sistema de auto-registro del KMC Parser.
"""
import unittest
import tempfile
import os
from pathlib import Path

# Cambiar importaciones relativas por absolutas
from kmc_parser.parser import KMCParser
from kmc_parser.core import registry

class TestAutoRegister(unittest.TestCase):
    def setUp(self):
        # Limpiar el registro antes de cada prueba
        registry.clear_handlers()
        registry.clear_plugins()
        
        self.test_dir = tempfile.mkdtemp()
        self.parser = KMCParser()
        
        # Registrar algunos handlers básicos para las pruebas
        registry.register_context_handler("project", lambda var: {
            "nombre": "Test Process",
            "version": "v1.0-test-process"
        }.get(var, f"<project:{var}>"))
        
        registry.register_metadata_handler("doc", lambda var: {
            "version": "1.0-test-process"
        }.get(var, f"<doc:{var}>"))
        
        registry.register_generative_handler("ai:gpt4", lambda name, prompt, format_type=None: 
            f"Contenido generado para {name}" + (f" en formato {format_type}" if format_type else ""))

    def tearDown(self):
        # Limpiar todo después de cada prueba
        registry.clear_all()
        
        if os.path.exists(self.test_dir):
            import shutil
            shutil.rmtree(self.test_dir)

    def test_process_document_native(self):
        """Prueba el procesamiento de un documento con handlers registrados"""
        contenido_test = """# Proyecto [[project:nombre]] [[project:version]]

<!-- KMC_DEFINITION FOR [{doc:resumen}]:
GENERATIVE_SOURCE = {{ai:gpt4:resumen}}
PROMPT = "Genera un resumen para el proyecto [[project:nombre]]"
FORMAT = "markdown"
-->

## Resumen
[{doc:resumen}]
"""
        resultado = self.parser.render(contenido_test)
        self.assertIn("# Proyecto Test Process v1.0-test-process", resultado)
        self.assertIn("Contenido generado para resumen en formato markdown", resultado)
        # La variable generativa no debe aparecer en el resultado final
        self.assertNotIn("{{ai:gpt4:resumen}}", resultado)
        # Los comentarios de definición deben eliminarse
        self.assertNotIn("KMC_DEFINITION", resultado)

    def test_process_document_no_custom_handlers(self):
        """Prueba el procesamiento sin handlers personalizados"""
        # Limpiar el registro para esta prueba
        registry.clear_all()
        
        contenido_test = """# Proyecto [[project:nombre]] v[{doc:version}]

{{ai:gpt4:resumen}}
<!-- KMC_DEFINITION FOR [{doc:analisis}]:
GENERATIVE_SOURCE = {{ai:gpt4:analisis}}
PROMPT = "Analiza los datos del proyecto"
-->

## Análisis
[{doc:analisis}]
"""
        # Sin handlers registrados, las variables deben quedarse como están
        resultado = self.parser.render(contenido_test)
        self.assertIn("# Proyecto [[project:nombre]] v[{doc:version}]", resultado)
        # Las variables generativas nunca se renderizan directamente
        self.assertIn("{{ai:gpt4:resumen}}", resultado)
        # Las variables de metadata sin handlers registrados permanecen igual
        self.assertIn("[{doc:analisis}]", resultado)
        # Los comentarios de definición deben eliminarse
        self.assertNotIn("KMC_DEFINITION", resultado)