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

KMC implementa una arquitectura expandible con autodetección de extensiones. Esta funcionalidad simplifica notablemente la integración de nuevos handlers, plugins y funcionalidades sin necesidad de modificar el código base.

*KMC implements an expandable architecture with extension autodetection. This functionality significantly simplifies the integration of new handlers, plugins, and features without the need to modify the base code.*

### Uso básico del parser con autodetección | Basic parser usage with autodetection

```python
from kmc_parser import KMCParser

# Inicializar el parser con autodetección habilitada (comportamiento por defecto)
# Initialize the parser with autodetection enabled (default behavior)
parser = KMCParser()

# Ejemplo de documento KMC | KMC document example
documento_markdown = """
# Proyecto: [[project:nombre]]
Autor: [[user:nombre]]

## Resumen Ejecutivo
<!-- KMC_DEFINITION FOR [{doc:resumen_ejecutivo}]:
GENERATIVE_SOURCE = {{ai:gpt4:generar_resumen}}
PROMPT = "Crear un resumen ejecutivo para el proyecto [[project:nombre]]."
-->
[{doc:resumen_ejecutivo}]

Este documento fue generado por [[user:nombre]].
"""

# Procesamiento del documento con handlers personalizados
# Document processing with custom handlers
resultado = parser.process_document(
    markdown_content=documento_markdown,
    default_handlers={
        "context": {
            "project": lambda var_name: "Proyecto KMC" if var_name == "nombre" else f"<project:{var_name}>",
            "user": lambda var_name: "Usuario Principal" if var_name == "nombre" else f"<user:{var_name}>"
        },
        "generative": {
            "ai:gpt4": lambda var: f"[Contenido generado para: {var.prompt}]"
        }
    }
)
print(resultado)
```

## Extendiendo KMC con Autodetección | Extending KMC with Autodetection

La forma recomendada de extender KMC es aprovechando su sistema de autodetección de extensiones:

*The recommended way to extend KMC is by leveraging its extension autodetection system:*

### 1. Creación de Extensiones Autodetectables | Creating Autodetectable Extensions

Para crear una extensión que sea detectada automáticamente, simplemente coloque su archivo en uno de los directorios de extensiones (`extensions/`, `user_extensions/`, `custom_handlers/` o `plugins/`).

*To create an extension that is automatically detected, simply place your file in one of the extension directories (`extensions/`, `user_extensions/`, `custom_handlers/` or `plugins/`).*

```python
# archivo: user_extensions/mi_handler_cliente.py

from kmc_parser.handlers.base import ContextHandler, context_handler

@context_handler("cliente")
class ClienteHandler(ContextHandler):
    """Handler para variables contextuales de cliente [[cliente:nombre]]"""
    
    def _get_context_value(self, var_name):
        datos_cliente = {
            "nombre": "Cliente Principal",
            "contacto": "cliente@example.com"
        }
        return datos_cliente.get(var_name, f"<cliente:{var_name}>")
```

### 2. Crear un Plugin Completo | Create a Complete Plugin

```python
# archivo: plugins/weather_plugin.py

from kmc_parser import KMCPlugin, registry
from kmc_parser.handlers.base import GenerativeHandler

class ApiWeatherHandler(GenerativeHandler):
    def _generate_content(self, var):
        # Implementación para obtener datos del clima
        return f"Datos del clima para: {var.prompt}"

class WeatherPlugin(KMCPlugin):
    def initialize(self):
        weather_handler = ApiWeatherHandler()
        registry.register_generative_handler("api:weather", weather_handler)
        return True
```

### 3. Verificar Extensiones Cargadas | Verify Loaded Extensions

```python
from kmc_parser import KMCParser
from kmc_parser.extensions.auto_discovery import ExtensionDiscovery
from kmc_parser.core import registry

# Ver qué extensiones se han descubierto
discovery = ExtensionDiscovery()
stats = discovery.discover_all_extensions()
print(f"Extensiones descubiertas: {stats}")

# Verificar handlers registrados
print(f"Handlers contextuales: {list(registry.context_handlers.keys())}")
print(f"Handlers generativos: {list(registry.generative_handlers.keys())}")
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
- `expansible_architecture/`: Ejemplos de uso de la arquitectura expandible con autodetección  
  *Examples of using the expandable architecture with autodetection*

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

2. **Preparar el KMC Parser con autodetección de extensiones**  
   *Set up the KMC Parser with extension autodetection*
   ```python
   from kmc_parser import KMCParser

   # El parser detectará automáticamente las extensiones disponibles
   parser = KMCParser()

   # Opcionalmente, definir handlers personalizados para comportamientos específicos
   custom_handlers = {
       "context": {
           "project": lambda var_name: {
               "nombre": "Proyecto Demo",
               "tipo": "Análisis de Mercado"
           }.get(var_name, f"<project:{var_name}>"),
           "user": lambda var_name: "Giorgio" if var_name == "nombre" else "giorgio@example.com"
       }
   }
   ```

3. **Procesar la plantilla**  
   *Process the template*
   ```python
   with open("plantilla.md", "r", encoding="utf-8") as f:
       contenido_markdown = f.read()

   # Procesa el documento con autodetección de extensiones
   resultado_renderizado = parser.process_document(
       markdown_content=contenido_markdown,
       default_handlers=custom_handlers  # Opcional: handlers personalizados
   )
   print(resultado_renderizado)
   ```

## Autodetección de Extensiones | Extension Autodetection

KMC incluye una capacidad de autodetección de extensiones que permite a los desarrolladores simplemente colocar sus archivos de extensión en directorios específicos sin necesidad de modificar manualmente el código base o registrar explícitamente cada handler o plugin.

*KMC includes an extension autodetection capability allowing developers to simply place their extension files in specific directories without needing to manually modify the base code or explicitly register each handler or plugin.*

### Componentes Principales del Sistema de Autodetección | Main Autodetection System Components

#### 1. Sistema de Descubrimiento de Extensiones (`ExtensionDiscovery`)

Este componente central se encarga de:
*This central component is responsible for:*

- Escanear directorios predefinidos en busca de extensiones  
  *Scanning predefined directories for extensions*
- Detectar clases que implementen las interfaces de handlers o plugins  
  *Detecting classes that implement handler or plugin interfaces*
- Registrar automáticamente los handlers y plugins encontrados  
  *Automatically registering the discovered handlers and plugins*
- Proporcionar información sobre las extensiones cargadas  
  *Providing information about loaded extensions*

Ubicación | Location: `kmc_parser/extensions/auto_discovery.py`

#### 2. Directorios Estandarizados | Standardized Directories

El sistema busca extensiones en los siguientes directorios:
*The system looks for extensions in the following directories:*

- `extensions/`: Extensiones propias del SDK  
  *SDK's own extensions*
- `user_extensions/`: Extensiones creadas por usuarios  
  *User-created extensions*
- `custom_handlers/`: Handlers personalizados  
  *Custom handlers*
- `plugins/`: Plugins adicionales  
  *Additional plugins*

#### 3. Integración con KMCParser | Integration with KMCParser

La clase `KMCParser` incluye:
*The `KMCParser` class includes:*

- Opción `auto_discover` en el constructor (habilitada por defecto)  
  *`auto_discover` option in the constructor (enabled by default)*
- Posibilidad de especificar directorios adicionales para buscar extensiones  
  *Ability to specify additional directories to look for extensions*
- Método `_auto_discover_extensions()` que ejecuta el proceso de descubrimiento  
  *`_auto_discover_extensions()` method that executes the discovery process*

```python
# Inicializar el parser con autodescubrimiento habilitado (por defecto)
# Initialize the parser with autodiscovery enabled (by default)
parser = KMCParser()

# O especificar un directorio personalizado
# Or specify a custom directory
parser = KMCParser(auto_discover=True, ext_directory="/ruta/personalizada")
```

### Implementación de Extensiones Autodetectables | Implementing Autodetectable Extensions

Para crear extensiones que sean detectables automáticamente:
*To create extensions that are automatically detectable:*

#### Handlers Autodetectables | Autodetectable Handlers

```python
from kmc_parser.handlers.base import ContextHandler, context_handler

@context_handler("mi_contexto")  # Decorador que registra el handler
class MiContextHandler(ContextHandler):
    """Handler para variables contextuales [[mi_contexto:nombre]]"""
    
    def _get_context_value(self, var_name):
        return f"Valor para {var_name}"

# Al guardar este archivo en 'user_extensions/' o 'custom_handlers/', 
# será detectado automáticamente al iniciar el parser.
```

#### Plugins Autodetectables | Autodetectable Plugins

```python
from kmc_parser.extensions.plugin_base import KMCPlugin
from kmc_parser.core import registry

class MiPlugin(KMCPlugin):
    """Un plugin personalizado que se registra automáticamente"""
    
    def initialize(self):
        registry.register_context_handler("mi_plugin_ctx", 
                                         lambda var: f"Valor de plugin para {var}")
        return True

# Al guardar este archivo en 'plugins/' o 'extensions/',
# será detectado automáticamente al iniciar el parser.
```

### Verificación de Descubrimiento | Discovery Verification

Para verificar qué extensiones se han descubierto:
*To verify which extensions have been discovered:*

```python
from kmc_parser import KMCParser
from kmc_parser.extensions.auto_discovery import ExtensionDiscovery

# Ver estadísticas de descubrimiento
discovery = ExtensionDiscovery()
stats = discovery.discover_all_extensions()
print(f"Extensiones descubiertas: {stats}")  # {'handlers': 5, 'plugins': 2}

# Las extensiones descubiertas se registran automáticamente en el registro central
from kmc_parser.core import registry
print(f"Handlers contextuales registrados: {list(registry.context_handlers.keys())}")
```

Para más ejemplos y usos avanzados, consulte los archivos en `examples/expansible_architecture/`.
*For more examples and advanced uses, check the files in `examples/expansible_architecture/`.*

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
  
- **07/05/2025**: Mejora en la documentación para enfocarse exclusivamente en el sistema de autodetección de extensiones como el método estándar.
  *Documentation improvement to focus exclusively on the extension autodetection system as the standard method.*
  
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
