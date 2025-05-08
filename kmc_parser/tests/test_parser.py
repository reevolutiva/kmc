"""
Tests para el parser KMC.
"""
import unittest

# Cambiar importaciones relativas por absolutas
from kmc_parser.parser import KMCParser
from kmc_parser.core import registry

class TestKMCParser(unittest.TestCase):
    def setUp(self):
        """Configuración inicial para cada test."""
        self.parser = KMCParser()
        
        # Registrar handlers de prueba
        registry.register_context_handler("project", lambda var: {
            "nombre": "Proyecto Demo",
            "datos_ventas": "100,000",
            "datos_competencia": "90,000"
        }.get(var, f"<project:{var}>"))
        
        registry.register_metadata_handler("doc", lambda var: {
            "version": "1.0"
        }.get(var, f"<doc:{var}>"))
        
        registry.register_generative_handler("ai:gpt4", lambda name, prompt, format_type=None: 
            f"Contenido generado para {name}" + (f" en formato {format_type}" if format_type else ""))
    
    def test_sintaxis_tradicional(self):
        """Prueba la sintaxis tradicional de KMC."""
        contenido = """# [[project:nombre]] v[{doc:version}]
        
{{ai:gpt4:analisis}}
<!-- AI_PROMPT FOR {{ai:gpt4:analisis}}: 
Analiza los datos:
[[project:datos_ventas]]
[[project:datos_competencia]]
-->"""
        
        esperado = """# Proyecto Demo v1.0
        
Contenido generado para analisis"""
        
        resultado = self.parser.render(contenido.strip())
        self.assertEqual(resultado.strip(), esperado.strip())

    def test_sintaxis_compacta(self):
        """Prueba la nueva sintaxis compacta de KMC."""
        contenido = """# [[project:nombre]] v[{doc:version}]
        
{{ai:gpt4:analisis}}
<!-- KMC {{ai:gpt4:analisis}}:\"Analiza los datos: [[project:datos_ventas]] vs [[project:datos_competencia]]\":FORMAT documento -->"""
        
        esperado = """# Proyecto Demo v1.0
        
Contenido generado para analisis en formato documento"""
        
        resultado = self.parser.render(contenido.strip())
        self.assertEqual(resultado.strip(), esperado.strip())

    def test_multiples_variables_generativas(self):
        """Prueba múltiples variables generativas con ambas sintaxis."""
        contenido = """# Reporte

{{ai:gpt4:resumen}}
<!-- KMC {{ai:gpt4:resumen}}:\"Genera un resumen\":FORMAT markdown -->

{{ai:gpt4:analisis}}
<!-- AI_PROMPT FOR {{ai:gpt4:analisis}}: 
Analiza los datos
-->

{{ai:gpt4:conclusion}}
<!-- KMC {{ai:gpt4:conclusion}}:\"Concluye el análisis\" -->"""
        
        resultado = self.parser.render(contenido)
        
        self.assertIn("Contenido generado para resumen en formato markdown", resultado)
        self.assertIn("Contenido generado para analisis", resultado)
        self.assertIn("Contenido generado para conclusion", resultado)

    def test_dependencias_entre_variables(self):
        """Prueba dependencias entre variables generativas."""
        contenido = """{{ai:gpt4:paso1}}
<!-- KMC {{ai:gpt4:paso1}}:\"Primer paso\":FORMAT lista -->

{{ai:gpt4:paso2}}
<!-- KMC {{ai:gpt4:paso2}}:\"Segundo paso usando {{ai:gpt4:paso1}}\" -->"""
        
        resultado = self.parser.render(contenido)
        
        self.assertIn("Contenido generado para paso1 en formato lista", resultado)
        self.assertIn("Contenido generado para paso2", resultado)

    def test_manejo_errores(self):
        """Prueba el manejo de errores en variables."""
        # Registrar un handler que lanza error
        registry.register_generative_handler("ai:error", 
            lambda name, prompt, format_type=None: (_ for _ in ()).throw(Exception("Error de prueba")))
        
        contenido = """{{ai:error:test}}
<!-- KMC {{ai:error:test}}:\"Esto debería fallar\" -->"""
        
        resultado = self.parser.render(contenido)
        self.assertIn("ERROR:ai:error:test", resultado)

if __name__ == '__main__':
    unittest.main()