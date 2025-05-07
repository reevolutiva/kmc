#!/usr/bin/env python
"""
Ejemplo de demostración de la arquitectura expandible del KMC Parser
"""
import os
import sys
import logging
import json

# Agregar la ruta del proyecto al path para poder importar kmc_parser
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from kmc_parser import (
    KMCParser, 
    registry, 
    plugin_manager, 
    ContextHandler, 
    MetadataHandler,
    GenerativeHandler,
    context_handler,
    metadata_handler,
    generative_handler,
    KMCPlugin
)
from kmc_parser.extensions.api_plugin import ExternalAPIsPlugin
from kmc_parser.handlers.context.project import ProjectHandler
from kmc_parser.handlers.metadata.doc import DocumentMetadataHandler
from kmc_parser.handlers.generative.ai.gpt4 import GPT4Handler
from kmc_parser.models import GenerativeVariable


# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("kmc.demo")


# Ejemplo 1: Usando los Handlers Predefinidos
def ejemplo_handlers_predefinidos():
    """Demuestra el uso de los handlers predefinidos incluidos con el KMC Parser."""
    print("\n=== EJEMPLO 1: USANDO HANDLERS PREDEFINIDOS ===")
    
    parser = KMCParser()
    
    # Configuración del ProjectHandler
    project_config = {
        "project_data": {
            "nombre": "Proyecto Demostrativo KMC",
            "descripcion": "Demostración de arquitectura expandible",
            "cliente": "Reevolutiva",
            "responsable": "Giorgio La Pietra",
            "fecha_inicio": "2025-05-07",
            "estado": "En desarrollo"
        }
    }
    
    # Configuración del DocumentMetadataHandler
    doc_config = {
        "metadata": {
            "version": "1.0.0",
            "titulo": "Demostración de Arquitectura Expandible",
            "autor": "KMC Team",
            "fecha": "2025-05-07",
            "categoria": "Documentación Técnica"
        }
    }
    
    # Configuración del GPT4Handler
    gpt4_config = {
        "temperature": 0.5,
        "max_tokens": 1000
    }
    
    # Registrar handlers en el registro central
    registry.register_context_handler("project", ProjectHandler(config=project_config))
    registry.register_metadata_handler("doc", DocumentMetadataHandler(config=doc_config))
    registry.register_generative_handler("ai:gpt4", GPT4Handler(config=gpt4_config))
    
    # Contenido markdown de ejemplo
    markdown = """# [[project:nombre]] v[{doc:version}]

## Descripción
[[project:descripcion]]

## Metadatos
- Autor: [{doc:autor}]
- Fecha: [{doc:fecha}]
- Cliente: [[project:cliente]]

## Resumen Ejecutivo
<!-- KMC_DEFINITION FOR [{doc:resumen_ejecutivo}]:
GENERATIVE_SOURCE = {{ai:gpt4:generar_resumen}}
PROMPT = "Genera un resumen ejecutivo para el proyecto [[project:nombre]] que es de tipo [[project:descripcion]]."
FORMAT = "text/plain"
-->

[{doc:resumen_ejecutivo}]

## Actividades Planificadas
{{ai:gpt4:actividades}}
<!-- AI_PROMPT FOR {{ai:gpt4:actividades}}:
Genera una lista de 3-5 actividades planificadas para el proyecto [[project:nombre]].
-->

## Estado Actual
- Estado del proyecto: [[project:estado]]
- Responsable: [[project:responsable]]
- Fecha de inicio: [[project:fecha_inicio]]
"""
    
    # Procesar el documento
    resultado = parser.process_document(markdown_content=markdown)
    
    print("=== DOCUMENTO RENDERIZADO ===")
    print(resultado)
    print("============================")


# Ejemplo 2: Creando un Custom Handler
@context_handler("user")
class UserHandler(ContextHandler):
    """
    Handler personalizado para variables contextuales de usuario [[user:nombre]]
    """
    def __init__(self, config=None):
        super().__init__(config)
        self.user_data = self.config.get("user_data", {
            "nombre": "Giorgio La Pietra",
            "email": "giorgio@reevolutiva.com",
            "rol": "CEO",
            "empresa": "Reevolutiva",
            "telefono": "+1234567890"
        })
    
    def _get_context_value(self, var_name):
        return self.user_data.get(var_name, f"<user:{var_name}>")


def ejemplo_custom_handler():
    """Demuestra la creación y uso de un handler personalizado."""
    print("\n=== EJEMPLO 2: USANDO UN HANDLER PERSONALIZADO ===")
    
    # Crear una nueva instancia de parser para este ejemplo
    parser = KMCParser()
    
    # Registrar nuestro handler personalizado en el registro central
    user_handler = UserHandler()
    registry.register_context_handler("user", user_handler)
    
    # Contenido markdown de ejemplo
    markdown = """# Informe de Usuario

## Datos del usuario
- Nombre: [[user:nombre]]
- Email: [[user:email]]
- Rol: [[user:rol]]
- Empresa: [[user:empresa]]
- Teléfono: [[user:telefono]]

## Actividades recientes
{{ai:gpt4:actividades_usuario}}
<!-- AI_PROMPT FOR {{ai:gpt4:actividades_usuario}}:
Genera una lista de 3 actividades recientes hipotéticas para [[user:nombre]] en su rol de [[user:rol]] en [[user:empresa]].
-->

## Datos de Contacto Adicionales
- Dirección: [[user:direccion]]
- LinkedIn: [[user:linkedin]]
"""
    
    # Procesar el documento
    resultado = parser.process_document(markdown_content=markdown)
    
    print("=== DOCUMENTO RENDERIZADO ===")
    print(resultado)
    print("============================")


# Ejemplo 3: Usando un Plugin
def ejemplo_uso_plugin():
    """Demuestra el uso del sistema de plugins."""
    print("\n=== EJEMPLO 3: USANDO EL SISTEMA DE PLUGINS ===")
    
    # Crear una nueva instancia de parser para este ejemplo
    parser = KMCParser()
    
    # Configurar y registrar el plugin de APIs externas
    api_plugin_config = {
        "weather_api_key": "demo_key",
        "weather_units": "metric",
        "stock_api_key": "demo_key"
    }
    
    external_apis_plugin = ExternalAPIsPlugin(config=api_plugin_config)
    plugin_manager.register_plugin(external_apis_plugin)
    
    # Imprimir información sobre plugins registrados
    print(f"Plugins registrados: {len(plugin_manager.get_all_plugins())}")
    for plugin in plugin_manager.get_all_plugins():
        print(f"  - {plugin.name} v{plugin.version}: {plugin.description}")
    
    # Contenido markdown de ejemplo que usa variables de API
    markdown = """# Informe de Mercado y Clima

## Condiciones Actuales

### Clima
{{api:weather:madrid}}
<!-- AI_PROMPT FOR {{api:weather:madrid}}:
Proporciona información del clima para la ciudad: Madrid
-->

{{api:weather:barcelona}}
<!-- AI_PROMPT FOR {{api:weather:barcelona}}:
Proporciona información del clima para la ciudad: Barcelona
-->

### Mercado Financiero
{{api:stock:AAPL}}
<!-- AI_PROMPT FOR {{api:stock:AAPL}}:
Proporciona información sobre la acción de Apple Inc.
-->

{{api:stock:MSFT}}
<!-- AI_PROMPT FOR {{api:stock:MSFT}}:
Proporciona información sobre la acción de Microsoft Corporation.
-->

## Análisis del Mercado
<!-- KMC_DEFINITION FOR [{doc:analisis_mercado}]:
GENERATIVE_SOURCE = {{ai:gpt4:generar_analisis}}
PROMPT = "Genera un breve análisis del mercado basado en los datos mostrados anteriormente."
FORMAT = "text/markdown"
-->

[{doc:analisis_mercado}]
"""
    
    # Procesar el documento
    resultado = parser.process_document(markdown_content=markdown)
    
    print("=== DOCUMENTO RENDERIZADO ===")
    print(resultado)
    print("============================")


# Ejemplo 4: Creando un Plugin Personalizado
class CalendarToolHandler(GenerativeHandler):
    """
    Handler para generar eventos de calendario.
    
    Este handler procesa variables como {{tool:calendar:eventos}}
    """
    __kmc_handler_type__ = "generative"
    __kmc_var_type__ = "tool:calendar"
    
    def _generate_content(self, var):
        """Genera un calendario de eventos basado en el prompt."""
        # Simulación simple - en producción podría conectarse a una API de calendario
        events = [
            {
                "title": "Reunión de Planificación",
                "date": "2025-05-08",
                "time": "10:00 - 11:30",
                "attendees": ["Giorgio", "Equipo de desarrollo"]
            },
            {
                "title": "Revisión de Sprint",
                "date": "2025-05-15",
                "time": "15:00 - 16:00",
                "attendees": ["Equipo completo"]
            },
            {
                "title": "Lanzamiento KMC 1.0",
                "date": "2025-05-30",
                "time": "09:00 - 17:00",
                "attendees": ["Todo el personal"]
            }
        ]
        
        # Formato markdown para eventos
        result = "### Próximos eventos\n\n"
        for event in events:
            result += f"**{event['title']}**\n"
            result += f"- Fecha: {event['date']}\n"
            result += f"- Hora: {event['time']}\n"
            result += f"- Asistentes: {', '.join(event['attendees'])}\n\n"
        
        return result


class ToolsPlugin(KMCPlugin):
    """Plugin que proporciona herramientas utilitarias para KMC."""
    __version__ = "0.1.0"
    
    def initialize(self):
        """Inicializa el plugin."""
        self.logger.info(f"Inicializando {self.name} v{self.version}")
        self.register_handlers()
        return True
    
    def register_handlers(self):
        """Registra los handlers proporcionados por este plugin."""
        calendar_handler = CalendarToolHandler()
        registry.register_generative_handler("tool:calendar", calendar_handler)
        return 1


def ejemplo_plugin_personalizado():
    """Demuestra la creación y uso de un plugin personalizado."""
    print("\n=== EJEMPLO 4: CREANDO Y USANDO UN PLUGIN PERSONALIZADO ===")
    
    # Crear una nueva instancia de parser para este ejemplo
    parser = KMCParser()
    
    # Crear y registrar el plugin personalizado
    tools_plugin = ToolsPlugin()
    plugin_manager.register_plugin(tools_plugin)
    
    # Contenido markdown de ejemplo
    markdown = """# Planificación del Proyecto

## Calendario de Eventos

{{tool:calendar:eventos}}
<!-- AI_PROMPT FOR {{tool:calendar:eventos}}:
Genera una lista de próximos eventos importantes del proyecto.
-->

## Tareas Pendientes

{{ai:gpt4:tareas}}
<!-- AI_PROMPT FOR {{ai:gpt4:tareas}}:
Genera una lista de tareas pendientes basadas en los eventos del calendario.
-->

## Notas Importantes
1. Todos los miembros del equipo deben revisar el calendario regularmente
2. Las reuniones virtuales requieren conexión 5 minutos antes
"""
    
    # Procesar el documento
    resultado = parser.process_document(markdown_content=markdown)
    
    print("=== DOCUMENTO RENDERIZADO ===")
    print(resultado)
    print("============================")


if __name__ == "__main__":
    print("==================================================")
    print("  DEMOSTRACIÓN DE LA ARQUITECTURA EXPANDIBLE KMC")
    print("==================================================")
    
    try:
        # Ejecutar ejemplos
        ejemplo_handlers_predefinidos()
        ejemplo_custom_handler()
        ejemplo_uso_plugin()
        ejemplo_plugin_personalizado()
        
        print("\n¡Demostración completada con éxito!")
    except Exception as e:
        logger.error(f"Error en la demostración: {str(e)}", exc_info=True)
    finally:
        # Limpiar plugins y handlers registrados
        plugin_manager.cleanup_all()