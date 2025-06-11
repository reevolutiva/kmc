"""
Ejemplo de integración de KMC con el frontend de Kimfe

Este módulo muestra cómo conectar el parser KMC con el flujo
de trabajo de plantillas en el frontend de Kimfe.
"""
import os
import sys
import json
from typing import Dict, Any, Optional

# Añadir el directorio principal al path para importar módulos del proyecto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.kmc.kmc_parser import KMCParser
from src.kmc.kmc_parser.integrations.itscop import ITSCOPIntegration


def process_template_for_frontend(
    template_content: str,
    project_id: str,
    user_id: str,
    org_id: str,
    document_metadata: Optional[Dict[str, Any]] = None,
    kb_ids: Optional[list] = None
) -> Dict[str, Any]:
    """
    Procesa una plantilla KMC para enviar al frontend
    
    Args:
        template_content: Contenido de la plantilla KMC
        project_id: ID del proyecto
        user_id: ID del usuario
        org_id: ID de la organización
        document_metadata: Metadata del documento (opcional)
        kb_ids: Lista de IDs de bases de conocimiento (opcional)
        
    Returns:
        Diccionario con información de la plantilla procesada
    """
    # Inicializar la integración con itscop
    integration = ITSCOPIntegration(
        project_id=project_id,
        user_id=user_id,
        org_id=org_id,
        kb_ids=kb_ids or []
    )
    
    # Cargar datos contextuales
    integration.load_context_data()
    
    # Registrar metadata del documento si está disponible
    if document_metadata:
        integration.register_document_metadata(document_metadata)
    
    # Extraer variables y estructura
    parser = KMCParser()
    
    # Extraer todas las variables contextuales
    context_vars = []
    for match in parser.context_pattern.finditer(template_content):
        var_type, var_name = match.groups()
        context_vars.append({
            "type": var_type,
            "name": var_name,
            "full": f"[[{var_type}:{var_name}]]"
        })
    
    # Extraer todas las variables de metadata
    metadata_vars = []
    for match in parser.metadata_pattern.finditer(template_content):
        var_type, var_name = match.groups()
        metadata_vars.append({
            "type": var_type,
            "name": var_name,
            "full": f"[{{{var_type}:{var_name}}}]"
        })
    
    # Extraer todas las variables generativas
    generative_vars = []
    prompts = parser.extract_prompts(template_content)
    
    for match in parser.generative_pattern.finditer(template_content):
        var_category, var_subtype_name = match.groups()
        var_full = f"{{{{{var_category}:{var_subtype_name}}}}}"
        
        # Extraer el prompt asociado si existe
        prompt = prompts.get(f"{var_category}:{var_subtype_name}", "")
        
        generative_vars.append({
            "category": var_category,
            "subtype_name": var_subtype_name,
            "prompt": prompt,
            "full": var_full
        })
    
    # Estructura para el frontend
    template_info = {
        "template": {
            "content": template_content,
            "variables": {
                "contextual": context_vars,
                "metadata": metadata_vars,
                "generative": generative_vars
            }
        },
        "project_id": project_id,
        "user_id": user_id,
        "org_id": org_id
    }
    
    # Si se desea renderizar también una vista previa parcial
    # (sin resolver variables generativas que podrían ser costosas)
    preview_content = integration.parser._resolve_context_variables(template_content)
    preview_content = integration.parser._resolve_metadata_variables(preview_content)
    
    template_info["preview"] = {
        "content": preview_content
    }
    
    return template_info


def save_template_structure(template_content: str, output_path: str):
    """
    Guarda la estructura de la plantilla en un archivo JSON
    para visualización o integración con el editor visual
    
    Args:
        template_content: Contenido de la plantilla KMC
        output_path: Ruta donde guardar el archivo JSON
    """
    template_info = process_template_for_frontend(
        template_content=template_content,
        project_id="demo_project",
        user_id="demo_user",
        org_id="demo_org",
        document_metadata={
            "title": "Plantilla de Demostración",
            "version": "1.0",
            "tipo_documento": "informe"
        }
    )
    
    # Guardar la estructura en un archivo JSON
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(template_info, f, ensure_ascii=False, indent=2)
    
    print(f"Estructura de plantilla guardada en: {output_path}")


if __name__ == "__main__":
    # Ejemplo de plantilla KMC
    template = """# [[project:nombre]] - Informe de Análisis

**Cliente:** [[org:nombre_empresa]]
**Fecha:** [[project:fecha_inicio]]
**Autor:** [[user:nombre_completo]]
**Versión:** [{doc:version}]

## Resumen Ejecutivo

{{ai:gpt4:resumen_ejecutivo}}
<!-- AI_PROMPT FOR {{ai:gpt4:resumen_ejecutivo}}: 
Genera un resumen ejecutivo conciso del proyecto [[project:nombre]].
Destaca el objetivo principal, el valor para el cliente y los resultados esperados.
Máximo 200 palabras.
-->

## Contexto del Proyecto

El proyecto [{doc:tipo_documento}] para [[org:nombre_empresa]] consiste en...

### Análisis de Requisitos

{{ai:summary:analisis_requisitos}}
<!-- AI_PROMPT FOR {{ai:summary:analisis_requisitos}}: 
Basándote en la documentación disponible, resume los requisitos principales
del proyecto. Organiza por prioridad y categoría.
-->

## Preguntas Frecuentes

{{ai:qa:faq}}
<!-- AI_PROMPT FOR {{ai:qa:faq}}:
Genera 3 preguntas frecuentes con sus respuestas sobre el proyecto.
Formato: Q1. Pregunta / A1. Respuesta
-->
"""
    
    # Guardar la estructura de la plantilla
    save_template_structure(template, "template_structure.json")