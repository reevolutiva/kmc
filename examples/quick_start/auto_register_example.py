"""
Ejemplo de uso de la característica de auto-registro de handlers del KMC Parser,
que ahora es la forma nativa y única de operar.
"""
import os
import sys

# Añadir la ruta principal al path para importar el paquete kmc_parser
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from kmc_parser import KMCParser
# from kmc_parser.integrations import LlamaIndexHandler # Descomentar si se usa LlamaIndex

# Definir rutas
TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), 'markdown_kmc.md')

def ejemplo_proceso_directo_con_kmc():
    """
    Ejemplo que muestra cómo utilizar el método process_document,
    que analiza, registra handlers automáticamente y renderiza en un solo paso.
    """
    # Inicializar parser
    parser = KMCParser()
    
    print("\n=== EJEMPLO DE PROCESO DIRECTO CON KMC ===\n")
    print("Usando el método process_document para analizar y renderizar en un solo paso...")
    
    # Opcional: Definir handlers personalizados para sobrescribir los automáticos (genéricos)
    # Optional: Define custom handlers to override the automatic (generic) ones
    custom_handlers = {
        "context": {
            "project": lambda var_name: {
                "nombre": "Proyecto KMC Simplificado",
                "fecha_inicio": "2025-05-07",
                "estado": "Activo"
            }.get(var_name, f"<project:{var_name}>"),
            "user": lambda var_name: "Usuario Demo" if var_name == "nombre" else f"<user:{var_name}>"
        },
        "metadata": {
            "doc": lambda var_name: "v4.0-directo" if var_name == "version" else f"<doc:{var_name}>"
        },
        "generative": {
            # Asumiendo que tienes un 'my_index' de LlamaIndex configurado
            # "ai:gpt4": LlamaIndexHandler(index=my_index),
            # Handler genérico si no se usa LlamaIndex o para otros tipos generativos:
            "ai:gpt4": lambda var: f"[Contenido IA para '{var.name}' con prompt: '{var.prompt}']"
        }
    }
    
    # Procesar el documento en un solo paso
    # El parser identificará las variables en TEMPLATE_PATH,
    # registrará los handlers (usando los de custom_handlers si coinciden, sino genéricos)
    # y luego renderizará el documento.
    # The parser will identify variables in TEMPLATE_PATH,
    # register handlers (using those from custom_handlers if they match, otherwise generic ones),
    # and then render the document.
    resultado = parser.process_document(
        markdown_path=TEMPLATE_PATH,
        default_handlers=custom_handlers
    )
    
    # Mostrar resultado
    print("\n=== PLANTILLA PROCESADA CON KMC (PROCESO DIRECTO) ===\n")
    print(resultado)
    print("\n=== FIN DE LA PLANTILLA ===\n")

    print("\n--- Ejemplo sin handlers personalizados (usará placeholders genéricos) ---")
    parser_sin_custom = KMCParser()
    resultado_sin_custom = parser_sin_custom.process_document(markdown_path=TEMPLATE_PATH)
    print("\n=== PLANTILLA PROCESADA (SIN HANDLERS PERSONALIZADOS) ===\n")
    print(resultado_sin_custom)
    print("\n=== FIN DE LA PLANTILLA ===\n")

if __name__ == "__main__":
    ejemplo_proceso_directo_con_kmc()
    
    print("\nVENTAJAS DEL ENFOQUE NATIVO DE AUTO-REGISTRO:")
    print("1. API del Parser KMC significativamente simplificada.")
    print("2. El desarrollador solo necesita usar `KMCParser()` y `parser.process_document()`.")
    print("3. Detección y registro de handlers completamente automático y transparente.")
    print("4. Flexibilidad mantenida: los handlers personalizados aún pueden ser proporcionados vía `default_handlers`.")
    print("5. Reducción drástica del código boilerplate necesario para usar el parser.")
    print("6. El SDK es más intuitivo y fácil de adoptar.")