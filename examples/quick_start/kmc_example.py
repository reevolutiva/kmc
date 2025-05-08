import os
import sys

# Añadir la ruta principal al path para importar el paquete kmc_parser
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from kmc_parser import KMCParser

# Definir rutas
TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), 'markdown_kmc.md')

# Definir handlers personalizados
# Estos handlers se utilizarán para resolver las variables en la plantilla
custom_handlers = {
    "context": {
        "project": lambda var_name: {
            "nombre": "Proyecto Demo",
            "fecha_inicio": "2025-05-07",
            "estado": "En desarrollo"
        }.get(var_name, f"<project:{var_name}>"),
        
        "org": lambda var_name: {
            "nombre_empresa": "Reevolutiva S.A.S."
        }.get(var_name, f"<org:{var_name}>"),
        
        "user": lambda var_name: {
            "nombre": "Giorgio La Pietra"
        }.get(var_name, f"<user:{var_name}>")
    },
    
    "metadata": {
        "doc": lambda var_name: {
            "version": "v2.0"
        }.get(var_name, f"<doc:{var_name}>")
    },
    
    "generative": {
        "ai:gpt4": lambda var: process_ai_variable(var),
        "ai:dalle": lambda var: process_image_variable(var)
    }
}

# Función auxiliar para procesar variables de IA
def process_ai_variable(var):
    """
    Handler para las variables generativas de tipo AI que procesa 
    la sintaxis KMC_DEFINITION
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

# Función auxiliar para procesar variables de imágenes
def process_image_variable(var):
    """Handler para variables generativas de imágenes"""
    return "[Imagen generada por AI: " + var.prompt + "]"

# Inicializar parser con auto-descubrimiento de extensiones habilitado
parser = KMCParser()

# Leer plantilla
with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
    plantilla = f.read()

# Procesar plantilla en un solo paso usando el método process_document
# Este método combina auto_register_handlers y render en una sola operación
resultado = parser.process_document(
    markdown_content=plantilla,
    default_handlers=custom_handlers
)

# Mostrar resultado
print("\n--- PLANTILLA PROCESADA CON KMC ---\n")
print(resultado)
print("\n--- FIN DE LA PLANTILLA ---\n")

print("Note que esta plantilla utiliza la sintaxis KMC_DEFINITION, que permite:")
print("- Definir variables de metadata vinculadas a fuentes generativas")
print("- Especificar instrucciones claras para generación de contenido")
print("- Definir formatos de salida específicos")
print("- Mantener documentos más organizados y mantenibles")