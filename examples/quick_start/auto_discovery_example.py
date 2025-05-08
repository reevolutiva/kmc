"""
Ejemplo de uso de la característica de auto-descubrimiento de handlers del KMC Parser,
que ahora es la forma estándar y recomendada de operar.
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
    que analiza, descubre handlers automáticamente y renderiza en un solo paso.
    """
    # Inicializar parser con auto-descubrimiento habilitado (comportamiento por defecto)
    parser = KMCParser()
    
    print("\n=== EJEMPLO DE PROCESO DIRECTO CON KMC (AUTODESCUBRIMIENTO) ===\n")
    print("Usando el método process_document para analizar y renderizar en un solo paso...")
    
    # Opcional: Definir handlers personalizados para sobrescribir los descubiertos automáticamente o para tipos no cubiertos.
    # Estos handlers tienen prioridad sobre los que se descubrirían automáticamente para los mismos tipos.
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
            "doc": lambda var_name: "v5.0-autodiscover" if var_name == "version" else f"<doc:{var_name}>"
        },
        "generative": {
            # Asumiendo que tienes un 'my_index' de LlamaIndex configurado y un handler autodetectable para él
            # "ai:gpt4": LlamaIndexHandler(index=my_index), 
            # Handler genérico si no se usa LlamaIndex o para otros tipos generativos no cubiertos por autodetección:
            "ai:gpt4": lambda var: f"[Contenido IA para '{var.name}' con prompt: '{var.prompt}']"
        }
    }
    
    # Procesar el documento en un solo paso
    # El parser identificará las variables en TEMPLATE_PATH,
    # descubrirá y registrará handlers automáticamente (los de `custom_handlers` tendrán prioridad si coinciden),
    # y luego renderizará el documento.
    resultado = parser.process_document(
        markdown_path=TEMPLATE_PATH,
        default_handlers=custom_handlers # `default_handlers` es opcional
    )
    
    # Mostrar resultado
    print("\n=== PLANTILLA PROCESADA CON KMC (AUTODESCUBRIMIENTO Y CUSTOM HANDLERS) ===\n")
    print(resultado)
    print("\n=== FIN DE LA PLANTILLA ===\n")

    print("\n--- Ejemplo solo con autodetección (sin handlers personalizados pasados a process_document) ---")
    # Si existen handlers en las carpetas de extensiones, se usarán.
    # Si no, se usarán placeholders genéricos para las variables no resueltas.
    parser_autodiscover_only = KMCParser()
    resultado_autodiscover_only = parser_autodiscover_only.process_document(markdown_path=TEMPLATE_PATH)
    print("\n=== PLANTILLA PROCESADA (SOLO AUTODESCUBRIMIENTO) ===\n")
    print(resultado_autodiscover_only)
    print("\n=== FIN DE LA PLANTILLA ===\n")

if __name__ == "__main__":
    ejemplo_proceso_directo_con_kmc()
    
    print("\nVENTAJAS DEL ENFOQUE DE AUTODESCUBRIMIENTO:")
    print("1. API del Parser KMC simplificada: `KMCParser()` y `parser.process_document()`.")
    print("2. No es necesario registrar handlers manualmente; solo colócalos en las carpetas de extensiones.")
    print("3. Detección y registro de handlers completamente automático y transparente.")
    print("4. Flexibilidad mantenida: los handlers personalizados aún pueden ser proporcionados vía `default_handlers` para casos específicos o para sobrescribir.")
    print("5. Código boilerplate reducido al mínimo para usar el parser.")
    print("6. El SDK es más intuitivo, fácil de adoptar y de extender.")
    print("7. Facilita la creación de ecosistemas de plugins y extensiones por la comunidad.")