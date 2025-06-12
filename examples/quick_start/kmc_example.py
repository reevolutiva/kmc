import os
import sys

# Añadir la ruta principal al path para importar el paquete kmc_parser
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from kmc_parser import KMCParser

# Definir rutas
TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), 'markdown_kmc.md')

# Inicializar parser
parser = KMCParser()

# Registrar handlers de ejemplo para las variables contextuales
parser.register_context_handler("project", lambda var: {
    "nombre": "Proyecto Demo",
    "fecha_inicio": "2025-05-07",
    "estado": "En desarrollo"
}.get(var, f"<project:{var}>"))

parser.register_context_handler("org", lambda var: {
    "nombre_empresa": "Reevolutiva S.A.S."
}.get(var, f"<org:{var}>"))

parser.register_context_handler("user", lambda var: {
    "nombre": "Giorgio La Pietra"
}.get(var, f"<user:{var}>"))

# Registrar handlers para las variables de metadata
parser.register_metadata_handler("doc", lambda var: {
    "version": "v2.0"
}.get(var, f"<doc:{var}>"))

# Registrar handlers para las variables generativas
def ai_handler(var):
    """
    Handler para las variables generativas de tipo AI que procesa 
    la nueva sintaxis KMC_DEFINITION
    """
    if var.name == "extract_summary":
        return "Este proyecto tiene como objetivo desarrollar una plataforma integrada para la gestión de documentos dinámicos con IA."
    elif var.name == "objectives":
        return """
- Implementar un parser de KMC completo y eficiente
- Integrar con múltiples modelos de IA para generación de contenido
- Desarrollar herramientas de validación de plantillas
- Crear una API para integración con aplicaciones terceras"""
    elif var.name == "conclusions":
        return "El proyecto avanza según lo planeado. La nueva sintaxis KMC_DEFINITION está mejorando significativamente la claridad y mantenibilidad de las plantillas."
    else:
        return f"<Contenido generado para {var.name}>"

# Registrar el handler para variables generativas de tipo AI
parser.register_generative_handler("ai:gpt4", ai_handler)

# Leer plantilla
with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
    plantilla = f.read()

# Procesar plantilla
resultado = parser.render(plantilla)

# Mostrar resultado
print("\n--- PLANTILLA PROCESADA CON KMC ---\n")
print(resultado)
print("\n--- FIN DE LA PLANTILLA ---\n")

print("Note que esta plantilla utiliza la nueva sintaxis KMC_DEFINITION, que permite:")
print("- Definir variables de metadata vinculadas a fuentes generativas")
print("- Especificar instrucciones claras para generación de contenido")
print("- Definir formatos de salida específicos")
print("- Mantener documentos más organizados y mantenibles")