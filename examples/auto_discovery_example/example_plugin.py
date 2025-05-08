"""
Plugin de ejemplo para demostrar la característica de autodetección de extensiones en KMC.

Este plugin implementa algunos handlers simples para variables contextuales,
de metadata y generativas, que pueden ser detectados automáticamente por KMC.
"""

from kmc_parser.extensions.plugin_base import KMCPlugin
from kmc_parser.handlers.base import context_handler, metadata_handler, generative_handler
from kmc_parser.handlers.base import ContextHandler, MetadataHandler, GenerativeHandler
from kmc_parser.core import registry

import logging
import datetime

class ExamplePluginHandler(ContextHandler):
    """Handler contextual de ejemplo que proporciona información básica."""
    
    def _get_context_value(self, var_name):
        """Devuelve el valor para una variable contextual."""
        values = {
            "nombre": "Plugin de ejemplo",
            "version": "1.0",
            "descripcion": "Este es un plugin de ejemplo que demuestra la autodetección"
        }
        return values.get(var_name, f"Variable '{var_name}' no encontrada")


class DateTimeHandler(ContextHandler):
    """Handler contextual que proporciona valores de fecha y hora."""
    
    def _get_context_value(self, var_name):
        """Devuelve información de fecha y hora según lo solicitado."""
        now = datetime.datetime.now()
        
        values = {
            "fecha": now.strftime("%Y-%m-%d"),
            "hora": now.strftime("%H:%M:%S"),
            "fecha_hora": now.strftime("%Y-%m-%d %H:%M:%S"),
            "dia": now.strftime("%A"),
            "mes": now.strftime("%B")
        }
        return values.get(var_name, f"Formato de fecha/hora '{var_name}' no reconocido")


@metadata_handler("ejemplo")
class ExampleMetadataHandler(MetadataHandler):
    """Handler de metadata de ejemplo que proporciona información para documentación."""
    
    def _get_metadata_value(self, var_name):
        """Devuelve el valor para una variable de metadata."""
        values = {
            "titulo": "Documentación de ejemplo",
            "autor": "Equipo KMC",
            "estado": "Borrador",
            "version": "0.9.0"
        }
        return values.get(var_name, f"Variable de metadata '{var_name}' no encontrada")


@generative_handler("demo:texto")
class DemoTextGenerator(GenerativeHandler):
    """Handler generativo de ejemplo que genera texto demo simple."""
    
    def _generate_content(self, var):
        """Genera contenido de texto demo basado en el prompt."""
        prompt = var.prompt or "Generar texto de ejemplo"
        format_type = var.format_type or "text"
        
        # Generar contenido demo basado en el formato solicitado
        if format_type == "markdown":
            return f"""## Contenido demo generado
            
**Prompt:** {prompt}

Este es un contenido de ejemplo generado por el plugin demo.
- Punto 1
- Punto 2
- Punto 3

> Este es un bloque de cita para demostración.
"""
        elif format_type == "json":
            return """{"resultado": "Esto es un ejemplo JSON", "items": [1, 2, 3], "éxito": true}"""
        else:
            return f"Texto de ejemplo generado en respuesta a: '{prompt}'"


@generative_handler("demo:lista")
class DemoListGenerator(GenerativeHandler):
    """Handler generativo de ejemplo que genera listas demo."""
    
    def _generate_content(self, var):
        """Genera listas demo basadas en el prompt."""
        items = ["Elemento 1", "Elemento 2", "Elemento 3", "Elemento 4", "Elemento 5"]
        
        # Si hay un prompt, usar la primera palabra como prefijo
        if var.prompt:
            prefix = var.prompt.split()[0] if var.prompt.split() else ""
            items = [f"{prefix} - {item}" for item in items]
            
        # Formatear según el tipo de formato solicitado
        if var.format_type == "markdown":
            return "\n".join([f"- {item}" for item in items])
        elif var.format_type == "numbered":
            return "\n".join([f"{i+1}. {item}" for i, item in enumerate(items)])
        else:
            return "\n".join(items)


class ExamplePlugin(KMCPlugin):
    """
    Plugin de ejemplo para KMC que demuestra la autodetección de extensiones.
    
    Este plugin registra varios handlers para demostrar diferentes tipos de
    variables y cómo pueden trabajar juntos dentro de un plugin cohesivo.
    """
    
    def initialize(self):
        """Inicializa el plugin registrando los handlers."""
        self.logger.info("Inicializando ExamplePlugin")
        
        # Registrar handlers contextuales
        registry.register_context_handler("ejemplo", ExamplePluginHandler())
        registry.register_context_handler("tiempo", DateTimeHandler())
        
        # Los otros handlers ya se registraron automáticamente mediante decoradores
        
        self.logger.info("ExamplePlugin inicializado correctamente")
        return True
    
    def shutdown(self):
        """Cierra el plugin (no hay recursos específicos que liberar en este ejemplo)."""
        self.logger.info("Cerrando ExamplePlugin")
        return True


# Notas sobre la detección automática:
#
# 1. La clase ExamplePlugin será detectada automáticamente por KMC cuando:
#    - Este archivo está en un directorio que KMC escanea (ej: plugins/, user_extensions/)
#    - KMC se instancia con auto_discover=True (comportamiento por defecto)
#
# 2. Las clases marcadas con decoradores (@metadata_handler, @generative_handler)
#    también se registran automáticamente cuando este módulo es importado.
#
# 3. El plugin puede registrar handlers adicionales (como ExamplePluginHandler
#    y DateTimeHandler) durante su inicialización.
#
# Esto permite una gran flexibilidad en cómo organizar y estructurar las extensiones,
# según la complejidad y requerimientos específicos.