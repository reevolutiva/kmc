"""
Ejemplo de integración de KMC con la infraestructura existente de Kimfe
"""
import os
import sys

# Añadir el directorio principal al path para importar módulos del proyecto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.kmc.kmc_parser import KMCParser
from src.kmc.kmc_parser.integrations import LlamaIndexHandler, LlamaIndexQAHandler
from src.utils.index import FAISSIndex
from src.utils.llamaindex import LlamaIndexMiddleware
from src.utils.documentBuilder import DocumentBuilder


def create_project_handler(project_id):
    """Crea un handler para variables de proyecto basado en el ID del proyecto"""
    # En un caso real, esto cargaría datos del proyecto desde la base de datos
    project_data = {
        "nombre": "Proyecto de Demostración KMC",
        "descripcion": "Este es un proyecto para demostrar la integración de KMC",
        "fecha_inicio": "2025-05-07",
        "cliente_id": "client123"
    }
    
    def handler(var_name):
        if var_name in project_data:
            return project_data[var_name]
        return f"[[project:{var_name} - No encontrado]]"
    
    return handler


def create_org_handler(org_id):
    """Crea un handler para variables de organización basado en el ID de la organización"""
    # En un caso real, esto cargaría datos de la organización desde la base de datos
    org_data = {
        "nombre_empresa": "Kimfe",
        "dominio": "kimfe.com",
        "industria": "Tecnología"
    }
    
    def handler(var_name):
        if var_name in org_data:
            return org_data[var_name]
        return f"[[org:{var_name} - No encontrado]]"
    
    return handler


def create_doc_handler(doc_data):
    """Crea un handler para variables de metadata de documento"""
    def handler(var_name):
        if var_name in doc_data:
            return doc_data[var_name]
        return f"[{doc:{var_name} - No encontrado}]"
    
    return handler


def create_llamaindex_handler(project_id=None, kb_ids=None):
    """
    Crea un handler para variables generativas basado en LlamaIndex
    Utiliza la infraestructura existente de Kimfe
    """
    # En un caso real, cargaríamos los documentos relevantes para el proyecto/KB
    
    # Usar la infraestructura de índice existente
    index = FAISSIndex()
    
    # Si se especifican KB IDs, añadirlos al índice
    if kb_ids:
        for kb_id in kb_ids:
            index.add_document(kb_id)
    
    # Crear un middleware de LlamaIndex para manejar las consultas
    middleware = LlamaIndexMiddleware(index=index.index)
    
    # Crear y configurar los handlers de LlamaIndex para diferentes tipos de consultas
    qa_handler = LlamaIndexQAHandler(query_engine=middleware.create_query_engine())
    summary_handler = LlamaIndexSummaryHandler(query_engine=middleware.create_summary_engine())
    
    return {
        "ai:gpt4": qa_handler,
        "ai:summary": summary_handler,
        "ai:qa": qa_handler
    }


def main(project_id="demo_project", documento_id="demo_doc"):
    """
    Ejemplo principal que muestra cómo usar KMC con la infraestructura existente de Kimfe
    """
    # Metadata del documento
    doc_data = {
        "numero_modulo": "3",
        "titulo_seccion": "Integración de KMC",
        "version": "1.0"
    }
    
    # Crear el parser KMC
    parser = KMCParser()
    
    # Registrar handlers para diferentes tipos de variables
    parser.register_context_handler("project", create_project_handler(project_id))
    parser.register_context_handler("org", create_org_handler("org123"))
    parser.register_metadata_handler("doc", create_doc_handler(doc_data))
    
    # Registrar los handlers de LlamaIndex para variables generativas
    llamaindex_handlers = create_llamaindex_handler(
        project_id=project_id, 
        kb_ids=["kb123", "kb456"]
    )
    
    for handler_type, handler in llamaindex_handlers.items():
        parser.register_generative_handler(handler_type, handler)
    
    # Documento de ejemplo en formato KMC
    kmc_document = """# [[project:nombre]]

**Cliente:** [[org:nombre_empresa]]
**Fecha:** [[project:fecha_inicio]]

## Módulo [{doc:numero_modulo}]: [{doc:titulo_seccion}]

### Resumen
{{ai:gpt4:resumen_modulo}}
<!-- AI_PROMPT FOR {{ai:gpt4:resumen_modulo}}: 
Genera un resumen conciso del módulo 3 sobre integración de KMC con Kimfe.
Destaca los componentes principales y su flujo de interacción. -->

### Preguntas Frecuentes
{{ai:qa:preguntas_frecuentes}}
<!-- AI_PROMPT FOR {{ai:qa:preguntas_frecuentes}}:
Genera 3 preguntas frecuentes con sus respuestas sobre cómo integrar KMC con LlamaIndex
en el contexto de un proyecto de Kimfe. Formato: Q1. Pregunta / A1. Respuesta -->

### Conclusión
{{ai:summary:conclusion}}
<!-- AI_PROMPT FOR {{ai:summary:conclusion}}:
Sintetiza la importancia de KMC para estandarizar la comunicación entre LLMs y plantillas
de documentos en el ecosistema Kimfe. Máximo 200 palabras. -->
"""
    
    # Procesar el documento
    resultado = parser.render(kmc_document)
    
    print("\n\n----- DOCUMENTO KMC PROCESADO -----\n")
    print(resultado)
    
    # En un caso real, aquí utilizaríamos DocumentBuilder para convertir a formato final
    doc_builder = DocumentBuilder()
    documento_final = doc_builder.build_from_markdown(resultado, documento_id)
    
    return documento_final


if __name__ == "__main__":
    main()