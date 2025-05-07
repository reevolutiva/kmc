import unittest
from kmc_parser.parser import KMCParser
from kmc_parser.models import KMCVariableDefinition, GenerativeVariable

class TestKMCDefinition(unittest.TestCase):
    """Pruebas para la funcionalidad de KMC_DEFINITION"""
    
    def setUp(self):
        """Configuración inicial para las pruebas"""
        self.parser = KMCParser()
        
        # Registrar handlers de prueba
        self.parser.register_context_handler("project", lambda var: {
            "nombre": "Proyecto Demo",
            "tipo": "Educativo"
        }.get(var, f"<project:{var}>"))
        
        self.parser.register_metadata_handler("kb", lambda var: {
            "contenido": "Este es un contenido de prueba para el módulo 1"
        }.get(var, f"<kb:{var}>"))
        
        # Handler generativo para pruebas
        def test_ai_handler(var: GenerativeVariable):
            if var.name == "extract_title":
                return "Título extraído del contenido"
            elif var.name == "gen_objectives":
                return "- Objetivo 1\n- Objetivo 2\n- Objetivo 3"
            return f"<generado:{var.name}>"
            
        self.parser.register_generative_handler("ai:gpt4", test_ai_handler)
    
    def test_parse_definition(self):
        """Prueba la extracción de definiciones desde un comentario"""
        comment = """KMC_DEFINITION FOR [{doc:titulo_modulo}]:
GENERATIVE_SOURCE = {{ai:gpt4:extract_title}}
PROMPT = "Extrae el título principal del módulo basándote en [{kb:contenido}]"
FORMAT = "text/plain; max_length=80"
"""
        definition = KMCVariableDefinition.from_comment(comment)
        
        self.assertIsNotNone(definition)
        self.assertEqual("doc:titulo_modulo", definition.metadata_var)
        self.assertEqual("ai:gpt4:extract_title", definition.generative_var)
        self.assertEqual("Extrae el título principal del módulo basándote en [{kb:contenido}]", definition.prompt)
        self.assertEqual("text/plain; max_length=80", definition.format)
        
        # Verificar que se detecten las dependencias
        self.assertIn("kb:contenido", definition.dependencies["metadata"])
    
    def test_render_with_definition(self):
        """Prueba el renderizado de un documento con definiciones KMC"""
        content = """# Módulo de Prueba
<!-- KMC_DEFINITION FOR [{doc:titulo}]:
GENERATIVE_SOURCE = {{ai:gpt4:extract_title}}
PROMPT = "Extrae el título del módulo del proyecto [[project:nombre]] basado en [{kb:contenido}]"
FORMAT = "text/plain"
-->

## [{doc:titulo}]

<!-- KMC_DEFINITION FOR [{doc:objetivos}]:
GENERATIVE_SOURCE = {{ai:gpt4:gen_objectives}}
PROMPT = "Genera objetivos de aprendizaje para [[project:tipo]]"
-->

### Objetivos:
[{doc:objetivos}]
"""
        
        rendered = self.parser.render(content)
        
        # Verificar que las definiciones se procesaron correctamente
        self.assertIn("## Título extraído del contenido", rendered)
        self.assertIn("### Objetivos:\n- Objetivo 1\n- Objetivo 2\n- Objetivo 3", rendered)
        
        # Verificar que los comentarios de definición se eliminaron
        self.assertNotIn("KMC_DEFINITION", rendered)
    
    def test_variable_dependencies(self):
        """Prueba la extracción de dependencias de variables en prompts"""
        definition = KMCVariableDefinition(
            "doc:resumen",
            "ai:gpt4:generar_resumen",
            "Genera un resumen para [[project:nombre]] considerando [{kb:datos}] y {{api:weather:clima}}",
            "text/plain"
        )
        
        # Verificar que todas las variables se detectaron correctamente
        self.assertIn("project:nombre", definition.dependencies["context"])
        self.assertIn("kb:datos", definition.dependencies["metadata"])
        self.assertIn("api:weather:clima", definition.dependencies["generative"])


if __name__ == "__main__":
    unittest.main()