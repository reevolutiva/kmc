# KMC - Kimfe Markdown Convention
_Última actualización: 7 de mayo de 2025 | Last update: May 7, 2025_

KMC es una convención de Markdown aumentado para crear plantillas inteligentes que se integran con sistemas de LLM, bases de conocimiento y APIs.

*KMC is an augmented Markdown convention for creating smart templates that integrate with LLM systems, knowledge bases, and APIs.*

## Estado actual | Current Status

KMC se encuentra en desarrollo activo y cuenta con los siguientes componentes:

*KMC is in active development and includes the following components:*

- **Core parser**: Implementado en `kmc_parser/parser.py` *(Implemented in `kmc_parser/parser.py`)*
- **Registro central**: Sistema de registro de handlers en `kmc_parser/core/registry.py` *(Central registry: Handler registration system in `kmc_parser/core/registry.py`)*
- **Handlers base**: Clases base para diferentes tipos de handlers en `kmc_parser/handlers/base.py` *(Base handlers: Base classes for different types of handlers in `kmc_parser/handlers/base.py`)*
- **Sistema de plugins**: Gestión de plugins en `kmc_parser/extensions/plugin_manager.py` *(Plugin system: Plugin management in `kmc_parser/extensions/plugin_manager.py`)*
- **Modelos de datos**: Definidos en `kmc_parser/models.py` *(Data models: Defined in `kmc_parser/models.py`)*
- **Integraciones**: Disponibles en `kmc_parser/integrations/` *(Integrations: Available in `kmc_parser/integrations/`)*
- **Documentación**: README.md principal y guía de sintaxis en `docs/SYNTAX.md` *(Documentation: Main README.md and syntax guide in `docs/SYNTAX.md`)*
- **Ejemplos de uso**: Varios ejemplos en la carpeta `examples/` *(Usage examples: Various examples in the `examples/` folder)*

## Visión general | Overview

KMC permite crear documentos Markdown que combinan:
*KMC enables the creation of Markdown documents that combine:*

- **Variables contextuales** (datos estáticos como información de proyecto o usuario)  
  *Contextual variables (static data like project or user information)*
- **Variables de metadata** (referencias a documentos o conocimiento)  
  *Metadata variables (references to documents or knowledge)*
- **Variables generativas** (contenido creado dinámicamente por LLMs u otros servicios)  
  *Generative variables (content dynamically created by LLMs or other services)*

Este enfoque unificado permite crear plantillas dinámicas, interactivas y adaptables que aprovechan toda la infraestructura existente de Kimfe.

*This unified approach allows creating dynamic, interactive, and adaptable templates that leverage the entire existing Kimfe infrastructure.*

## Características principales | Main Features

- **Sintaxis clara y consistente** que diferencia entre tipos de variables  
  *Clear and consistent syntax that differentiates between variable types*
- **Sistema modular extensible** para añadir nuevos tipos de variables y handlers  
  *Extensible modular system for adding new types of variables and handlers*
- **Arquitectura expandible** con registro centralizado y sistema de plugins  
  *Expandable architecture with centralized registry and plugin system*
- **Integración con LlamaIndex** para búsqueda semántica y generación basada en conocimiento  
  *Integration with LlamaIndex for semantic search and knowledge-based generation*
- **Soporte para encadenamiento de variables** para workflows complejos  
  *Support for variable chaining for complex workflows*
- **Compatible con Markdown estándar** - funciona con todos los visualizadores de Markdown  
  *Compatible with standard Markdown - works with all Markdown viewers*
- **Definiciones integradas de variables** - sintaxis declarativa que relaciona variables de metadatos con fuentes generativas  
  *Integrated variable definitions - declarative syntax that relates metadata variables with generative sources*
- **Reglas de renderizado claras** - variables con `[]` se renderizan una vez procesadas, variables con `{}` nunca se renderizan directamente  
  *Clear rendering rules - variables with `[]` are rendered once processed, variables with `{}` are never rendered directly*

## Arquitectura | Architecture

KMC consta de varios componentes:
*KMC consists of several components:*

1. **Parser KMC** (`kmc_parser/parser.py`): Núcleo que analiza y procesa documentos KMC  
   *KMC Parser (`kmc_parser/parser.py`): Core that analyzes and processes KMC documents*

2. **Sistema de Registro Centralizado** (`kmc_parser/core/registry.py`): Punto único para registrar y recuperar handlers de variables  
   *Centralized Registry System (`kmc_parser/core/registry.py`): Single point for registering and retrieving variable handlers*
   ```python
   from kmc_parser import registry
   
   # Registrar un handler para variables de proyecto
   registry.register_context_handler("project", mi_handler_proyecto)
   
   # Obtener un handler registrado
   handler = registry.get_context_handler("project")
   ```

3. **Jerarquía de Handlers** (`kmc_parser/handlers/base.py`): Clases base para diferentes tipos de variables  
   *Handler Hierarchy (`kmc_parser/handlers/base.py`): Base classes for different types of variables*
   ```python
   from kmc_parser import ContextHandler, context_handler
   
   @context_handler("user")
   class UserHandler(ContextHandler):
       def _get_context_value(self, var_name):
           # Implementación para obtener valor de variable contextual
           return f"Valor para {var_name}"
   ```

4. **Sistema de Plugins** (`kmc_parser/extensions/plugin_manager.py`): Marco para extender la funcionalidad del parser  
   *Plugin System (`kmc_parser/extensions/plugin_manager.py`): Framework for extending parser functionality*
   ```python
   from kmc_parser import KMCPlugin, plugin_manager
   
   class MiPlugin(KMCPlugin):
       def initialize(self):
           # Configurar recursos y registrar handlers
           return True
   
   # Registrar el plugin
   plugin_manager.register_plugin(MiPlugin())
   ```

5. **Integraciones** (`kmc_parser/integrations/`): Conectores para frameworks externos (LlamaIndex, etc.)  
   *Integrations (`kmc_parser/integrations/`): Connectors for external frameworks (LlamaIndex, etc.)*

6. **Sistema de Definición de Variables** (`kmc_parser/models.py:KMCVariableDefinition`): Implementa la sintaxis declarativa para relacionar variables  
   *Variable Definition System (`kmc_parser/models.py:KMCVariableDefinition`): Implements declarative syntax to relate variables*

## Sintaxis básica | Basic Syntax

### Variables contextuales | Contextual variables: `[[tipo:nombre]]`
```markdown
[[project:nombre]]    # Nombre del proyecto actual | Current project name
[[user:email]]        # Email del usuario actual | Current user's email
[[org:nombre_empresa]] # Nombre de la organización | Organization name
```

### Variables de metadata | Metadata variables: `[{tipo:nombre}]`
```markdown
[{doc:version}]       # Versión del documento actual | Current document version
[{kb:cita_1}]         # Referencia a la base de conocimiento | Reference to knowledge base
```

### Variables generativas | Generative variables: `{{categoria:subtipo:nombre}}`
```markdown
{{ai:gpt4:resumen}}   # Resumen generado por GPT-4 | Summary generated by GPT-4
{{api:weather:clima}} # Datos obtenidos de una API del clima | Data obtained from weather API
```

### Sistema de definición de variables (KMC_DEFINITION) | Variable Definition System
```markdown
<!-- KMC_DEFINITION FOR [{doc:titulo_modulo}]:
GENERATIVE_SOURCE = {{ai:gpt4:extract_title}}
PROMPT = "Extrae el título principal del módulo basándote en [{kb:contenido}]"
FORMAT = "text/plain; max_length=80"
-->

## [{doc:titulo_modulo}]
```

Esta sintaxis declarativa ofrece varias ventajas:
*This declarative syntax offers several advantages:*

- Define claramente la relación entre variables de metadata y fuentes generativas  
  *Clearly defines the relationship between metadata variables and generative sources*
- Concentra toda la configuración en un solo lugar (autocontenida)  
  *Concentrates all configuration in one place (self-contained)*
- Mejora la trazabilidad de las variables y sus dependencias  
  *Improves the traceability of variables and their dependencies*
- Facilita la reutilización de patrones comunes en plantillas  
  *Facilitates the reuse of common patterns in templates*

Para más información sobre esta sintaxis, consulta la sección 2.3 en la [Guía de Sintaxis](docs/SYNTAX.md).  
*For more information about this syntax, see section 2.3 in the [Syntax Guide](docs/SYNTAX.md).*

## Instalación | Installation

```bash
pip install -e .
```

Para instalar con dependencias opcionales:  
*To install with optional dependencies:*
```bash
pip install -e ".[langchain,crewai]"
```

## Uso básico | Basic Usage

El KMC Parser ahora incorpora una arquitectura expandible que facilita la extensión del sistema y la integración de nuevas funcionalidades a través del registro centralizado y el sistema de plugins.

*The KMC Parser now incorporates an expandable architecture that facilitates system extension and integration of new functionalities through the centralized registry and plugin system.*

### Uso simple con registro automático | Simple usage with automatic registration

```python
from kmc_parser import KMCParser

# Crear el parser | Create the parser
parser = KMCParser()

# Contenido del documento KMC | KMC document content
documento_markdown = """
# Proyecto: [[project:nombre]]
Tipo: [[project:tipo]]
Versión del Documento: [{doc:version}]
Autor: [[user:nombre]]

## Resumen Ejecutivo
<!-- KMC_DEFINITION FOR [{doc:resumen_ejecutivo}]:
GENERATIVE_SOURCE = {{ai:gpt4:generar_resumen}}
PROMPT = "Crear un resumen ejecutivo para el proyecto [[project:nombre]] sobre [[project:tipo]]."
-->
[{doc:resumen_ejecutivo}]

## Tareas Pendientes
{{ai:gpt4:listar_tareas}}
<!-- AI_PROMPT FOR {{ai:gpt4:listar_tareas}}:
Listar tareas pendientes para un proyecto de [[project:tipo]].
-->

Este documento fue generado por [[user:nombre]].
"""

# El parser registrará automáticamente los handlers necesarios
stats = parser.auto_register_handlers(markdown_content=documento_markdown)

# También puedes proporcionar handlers personalizados
custom_handlers = {
    "context": {
        "project": lambda var_name: {
            "nombre": "Proyecto KMC Expandible",
            "tipo": "Arquitectura de SDK"
        }.get(var_name, f"<project:{var_name}>"),
        "user": lambda var_name: "Usuario Principal" if var_name == "nombre" else f"<user:{var_name}>"
    }
}

# Procesar el documento
resultado_renderizado = parser.process_document(
    markdown_content=documento_markdown, 
    default_handlers=custom_handlers
)
print(resultado_renderizado)
```

### Uso avanzado con handlers y plugins | Advanced usage with handlers and plugins

```python
from kmc_parser import KMCParser, registry, ContextHandler, plugin_manager

# Creando un handler personalizado
class ProjectHandler(ContextHandler):
    def __init__(self, config=None):
        super().__init__(config)
        self.project_data = self.config.get("project_data", {
            "nombre": "Proyecto KMC",
            "tipo": "SDK para procesamiento de documentos",
            "estado": "En desarrollo"
        })
    
    def _get_context_value(self, var_name):
        return self.project_data.get(var_name, f"<project:{var_name}>")

# Registrando el handler en el registro central
registry.register_context_handler("project", ProjectHandler())

# El parser utilizará automáticamente los handlers registrados
parser = KMCParser()
resultado = parser.process_document(markdown_content=documento_markdown)
```

## Extendiendo KMC | Extending KMC

La arquitectura expandible de KMC facilita la creación de extensiones:
*The expandable architecture of KMC facilitates creating extensions:*

1. **Crear un handler personalizado | Create a custom handler**
```python
from kmc_parser import ContextHandler, context_handler

@context_handler("cliente")
class ClienteHandler(ContextHandler):
    """Handler para variables contextuales de cliente [[cliente:nombre]]"""
    
    def _get_context_value(self, var_name):
        # Implementar lógica para obtener datos del cliente
        return f"Valor para cliente:{var_name}"
```

2. **Crear un plugin completo | Create a complete plugin**
```python
from kmc_parser import KMCPlugin, registry
from kmc_parser.handlers.base import GenerativeHandler

class ApiWeatherHandler(GenerativeHandler):
    def _generate_content(self, var):
        # Implementación para obtener datos del clima
        return f"Datos del clima para: {var.prompt}"

class WeatherPlugin(KMCPlugin):
    def initialize(self):
        self.register_handlers()
        return True
    
    def register_handlers(self):
        weather_handler = ApiWeatherHandler()
        registry.register_generative_handler("api:weather", weather_handler)
        return 1
```

Para más ejemplos de extensión de KMC, consulte la carpeta `examples/expansible_architecture/`.
*For more examples of extending KMC, check the `examples/expansible_architecture/` folder.*

## Documentación | Documentation

Para más información sobre la sintaxis y uso avanzado:  
*For more information on syntax and advanced usage:*
- [Guía de Sintaxis | Syntax Guide](docs/SYNTAX.md)

## Ejemplos | Examples

El directorio `examples/` contiene varios ejemplos de uso:  
*The `examples/` directory contains several usage examples:*
- `kimfe_integration.py`: Integración con la infraestructura existente  
  *Integration with existing infrastructure*
- `frontend_integration.py`: Integración con el frontend  
  *Integration with the frontend*
- `quick_start/`: Ejemplos básicos para empezar a usar KMC  
  *Basic examples to start using KMC*
- `expansible_architecture/`: Ejemplos de uso de la nueva arquitectura expandible  
  *Examples of using the new expandable architecture*

## Flujo de trabajo y arquitectura | Workflow and Architecture

KMC está diseñado para proporcionar un flujo de trabajo claro y modular para desarrolladores:  
*KMC is designed to provide a clear and modular workflow for developers:*

### Flujo de trabajo para desarrolladores | Developer Workflow

1. **Definir las variables en el documento Markdown** utilizando la sintaxis de KMC  
   *Define variables in the Markdown document* using KMC syntax
   ```markdown
   # Informe de [[project:tipo]]
   
   <!-- KMC_DEFINITION FOR [{doc:resumen}]:
   GENERATIVE_SOURCE = {{ai:gpt4:resumen}}
   PROMPT = "Resume los aspectos principales de [[project:nombre]]"
   FORMAT = "markdown"
   -->
   
   ## Resumen ejecutivo
   [{doc:resumen}]
   
   ## Datos de contacto
   Responsable: [[user:nombre]] ([[user:email]])
   ```

2. **Preparar el KMC Parser y definir handlers personalizados (opcional)**  
   *Set up the KMC Parser and define custom handlers (optional)*
   ```python
   from kmc_parser import KMCParser

   parser = KMCParser()

   # Opcional: Define handlers personalizados si necesitas un comportamiento específico.
   # Si no, el parser usará handlers genéricos (placeholders).
   # Optional: Define custom handlers if you need specific behavior.
   # Otherwise, the parser will use generic (placeholder) handlers.
   custom_handlers = {
       "context": {
           "project": lambda var_name: {
               "nombre": "Proyecto Demo Workflow",
               "tipo": "Análisis de Mercado Avanzado"
           }.get(var_name, f"<project:{var_name}>"),
           "user": lambda var_name: "Giorgio" if var_name == "nombre" else \
                                 "giorgio@reevolutiva.com" if var_name == "email" else f"<user:{var_name}>"
       },
       "generative": {
           "ai:gpt4": lambda var: f"[Contenido AI para '{var.name}' con prompt: '{var.prompt}']"
       }
       # Añade otros handlers para 'metadata' o más tipos si es necesario
   }
   ```

3. **Procesar la plantilla**  
   *Process the template*
   ```python
   with open("plantilla.md", "r", encoding="utf-8") as f:
       contenido_markdown = f.read()

   # Procesa el documento. Los handlers se registran automáticamente.
   # Process the document. Handlers are registered automatically.
   resultado_renderizado = parser.process_document(
       markdown_content=contenido_markdown,
       default_handlers=custom_handlers # Pasa tus handlers personalizados aquí
   )
   print(resultado_renderizado)
   ```
## Reutilización de variables y métodos por proyecto | Reuse of Variables and Methods by Project

El SDK de KMC permite a los desarrolladores gestionar variables y métodos de manera centralizada:  
*The KMC SDK allows developers to manage variables and methods centrally:*

1. **Handlers centralizados | Centralized Handlers:**
   ```python
   class ProjectHandlers:
       def __init__(self, project_id):
           self.project_id = project_id
           self.data = self.load_project_data(project_id)

       def load_project_data(self, project_id):
           # Cargar datos del proyecto desde una base de datos o archivo
           # Load project data from a database or file
           return {"nombre": "Proyecto Alpha", "tipo": "Investigación"}

       def handler(self, var_name):
           return self.data.get(var_name, f"<project:{var_name}>")
   ```

2. **Configuración por proyecto | Project Configuration:**
   ```python
   PROJECTS = {
       "project123": {
           "variables": {
               "nombre": "Proyecto Alpha",
               "cliente": "Empresa XYZ"
           }
       },
       "project456": {
           "variables": {
               "nombre": "Proyecto Beta",
               "cliente": "Corporación ABC"
           }
       }
   }

   def load_project_config(project_id):
       return PROJECTS.get(project_id, {"variables": {}})
   ```

## Bitácora de cambios | Changelog

- **07/05/2025**: Actualización de la documentación para incluir soporte bilingüe (español/inglés) y clarificar la nueva sintaxis KMC_DEFINITION.  
  *Documentation update to include bilingual support (Spanish/English) and clarify the new KMC_DEFINITION syntax.*
  
- **08/05/2025**: Mejoras en la lógica del modelo:  
  *Improvements in model logic:*
  - Implementación de un sistema de registro dinámico de handlers.  
    *Implementation of a dynamic handler registration system.*
  - Integración con configuración centralizada de proyectos.  
    *Integration with centralized project configuration.*
  - Extensión del patrón Factory para nuevos tipos de handlers.  
    *Extension of the Factory pattern for new types of handlers.*
  - Optimización del proceso de resolución de variables en cascada.  
    *Optimization of the cascade variable resolution process.*
  - Nueva sintaxis KMC_DEFINITION para definiciones declarativas de variables.  
    *New KMC_DEFINITION syntax for declarative variable definitions.*
  
- **07/05/2025**: Implementación de la arquitectura expandible:
  *Implementation of the expandable architecture:*
  - Nuevo sistema de registro centralizado (`registry.py`).
    *New centralized registry system (`registry.py`).*
  - Jerarquía de handlers base para diferentes tipos de variables.
    *Base handler hierarchy for different variable types.*
  - Sistema de plugins para extender la funcionalidad.
    *Plugin system to extend functionality.*
  - Integración de la arquitectura expandible con el parser existente.
    *Integration of the expandable architecture with the existing parser.*

- **08/05/2025**: Implementación de autodetección de extensiones:
  *Implementation of extension autodetection:*
  - Nuevo sistema de descubrimiento de extensiones (`ExtensionDiscovery`).
    *New extension discovery system (`ExtensionDiscovery`).*
  - Métodos `_scan_directory_for_handlers` y `_scan_directory_for_plugins` implementados.
    *Implemented `_scan_directory_for_handlers` and `_scan_directory_for_plugins` methods.*
  - Integración completa con `KMCParser` para autodetección de extensiones.
    *Full integration with `KMCParser` for extension autodetection.*
  - Documentación y ejemplos actualizados para reflejar la autodetección completa.
    *Documentation and examples updated to reflect complete autodetection.*
