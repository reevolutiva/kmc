"""
Tests para las funcionalidades de auto-registro de handlers del KMC Parser.
"""
import unittest
import tempfile
import os
from ..parser import KMCParser

class TestAutoRegister(unittest.TestCase):
    def setUp(self):
        """Configuración inicial para cada test."""
        self.parser = KMCParser()
        
        # Crear un archivo temporal con contenido KMC para pruebas
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.md')
        self.temp_file.write("""# [[project:nombre]] v[{doc:version}]

## Resumen Ejecutivo
{{ai:gpt4:resumen}}
<!-- KMC_DEFINITION FOR [{doc:resumen}]:
GENERATIVE_SOURCE = {{ai:gpt4:extract_summary}}
PROMPT = "Genera un resumen para [[project:nombre]]"
FORMAT = "text/plain"
-->

## Objetivos
{{ai:gpt4:objetivos}}
<!-- AI_PROMPT FOR {{ai:gpt4:objetivos}}: 
Enumera los objetivos principales de [[project:nombre]]
-->

## Contacto
[[user:nombre]] ([[user:email]])

## Conclusiones
[{doc:resumen}]
""")
        self.temp_file.close()
    
    def tearDown(self):
        """Limpieza después de cada test."""
        os.unlink(self.temp_file.name)
    
    def test_auto_register_handlers_file_native(self):
        """Prueba del método auto_register_handlers (ahora nativo) con archivo markdown."""
        parser = KMCParser() # Nueva instancia para cada prueba específica
        stats = parser.auto_register_handlers(markdown_path=self.temp_file.name)
        
        self.assertIn("project", stats["context"])
        self.assertIn("user", stats["context"])
        self.assertIn("doc", stats["metadata"])
        self.assertIn("ai:gpt4", stats["generative"])
        
        # Verificar que los handlers se registraron internamente
        self.assertIn("project", parser.context_handlers)
        self.assertIn("user", parser.context_handlers)
        self.assertIn("doc", parser.metadata_handlers)
        self.assertIn("ai:gpt4", parser.generative_handlers)
    
    def test_auto_register_handlers_content_native(self):
        """Prueba del método auto_register_handlers (ahora nativo) con contenido markdown directo."""
        parser = KMCParser()
        content = """# [[project:nombre_test]]
[{doc:version_test}]
{{ai:gpt4:test_content_var}}"""
        
        stats = parser.auto_register_handlers(markdown_content=content)
        
        self.assertIn("project", stats["context"])
        self.assertIn("doc", stats["metadata"])
        self.assertIn("ai:gpt4", stats["generative"])
        self.assertIn("project", parser.context_handlers)
        self.assertIn("doc", parser.metadata_handlers)
        self.assertIn("ai:gpt4", parser.generative_handlers)
    
    def test_auto_register_with_default_handlers_native(self):
        """Prueba del auto-registro (nativo) con handlers predefinidos."""
        parser = KMCParser()
        custom_handlers = {
            "context": {
                "project": lambda var_name: "Proyecto Test Custom"
            },
            "metadata": {
                "doc": lambda var_name: "v1.0-test-custom"
            },
            "generative": {
                "ai:gpt4": lambda var_obj: f"Custom AI content for {var_obj.name}"
            }
        }
        
        parser.auto_register_handlers(
            markdown_path=self.temp_file.name,
            default_handlers=custom_handlers
        )
        
        self.assertEqual(parser.context_handlers["project"]("nombre"), "Proyecto Test Custom")
        self.assertEqual(parser.metadata_handlers["doc"]("version"), "v1.0-test-custom")
        
        # Para probar el handler generativo, necesitamos simular una variable generativa
        from src.kmc.kmc_parser.models import GenerativeVariable
        test_gen_var = GenerativeVariable(category="ai", subtype="gpt4", name="resumen")
        self.assertEqual(parser.generative_handlers["ai:gpt4"](test_gen_var), "Custom AI content for resumen")

    def test_process_document_native(self):
        """Prueba del método simplificado process_document (con auto-registro nativo)."""
        parser = KMCParser()
        custom_handlers = {
            "context": {
                "project": lambda var_name: "Proyecto Test Process" if var_name == "nombre" else f"<project:{var_name}>",
                "user": lambda var_name: "Usuario Test Process" if var_name == "nombre" else f"<user:{var_name}>"
            },
            "metadata": {
                "doc": lambda var_name: "v1.0-test-process" if var_name == "version" else f"<doc:{var_name}>"
            },
            "generative": {
                # Este handler se usará para la KMC_DEFINITION de [{doc:resumen}]
                "ai:gpt4:extract_summary": lambda var_obj: f"Resumen generado para {var_obj.prompt}", 
                # Este handler se usará para {{ai:gpt4:objetivos}} que tiene un AI_PROMPT
                "ai:gpt4:objetivos": lambda var_obj: f"Objetivos generados para {var_obj.prompt}" 
            }
        }
        
        resultado = parser.process_document(
            markdown_path=self.temp_file.name,
            default_handlers=custom_handlers
        )
        
        self.assertIn("# Proyecto Test Process v1.0-test-process", resultado)
        self.assertIn("Usuario Test Process", resultado)
        # Verificamos que el contenido de la KMC_DEFINITION se haya renderizado
        self.assertIn("Resumen generado para Genera un resumen para Proyecto Test Process", resultado)
        # Verificamos que el contenido del AI_PROMPT se haya renderizado (aunque la variable {{}} no se muestra)
        # El handler de {{ai:gpt4:objetivos}} no se invoca directamente en el renderizado final,
        # sino que su prompt se resuelve. Las variables generativas no se reemplazan directamente.
        # Por lo tanto, no buscamos "Objetivos generados para..." en el resultado final.
        self.assertNotIn("{{ai:gpt4", resultado) 
        self.assertNotIn("<!-- KMC_DEFINITION", resultado)
        self.assertNotIn("<!-- AI_PROMPT", resultado)

    def test_process_document_no_custom_handlers(self):
        """Prueba process_document sin handlers personalizados, usando solo genéricos."""
        parser = KMCParser()
        resultado = parser.process_document(markdown_path=self.temp_file.name)

        # Verificar que los placeholders genéricos están presentes
        self.assertIn("# <project:nombre> v<doc:version>", resultado)
        self.assertIn("<user:nombre> (<user:email>)", resultado)
        # La KMC_DEFINITION usará un handler genérico para la fuente generativa
        # y el prompt también usará placeholders para las variables internas.
        self.assertIn("<Contenido generativo para ai:gpt4:extract_summary>", resultado)
        self.assertNotIn("{{ai:gpt4", resultado)
        self.assertNotIn("<!-- KMC_DEFINITION", resultado)
        self.assertNotIn("<!-- AI_PROMPT", resultado)

if __name__ == '__main__':
    unittest.main()