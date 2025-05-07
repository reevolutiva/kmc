# KMC - Kimfe Markdown Convention
_Última actualización: 7 de mayo de 2025 | Last update: May 7, 2025_

KMC es una convención de Markdown aumentado para crear plantillas inteligentes que se integran con sistemas de LLM, bases de conocimiento y APIs.

*KMC is an augmented Markdown convention for creating smart templates that integrate with LLM systems, knowledge bases, and APIs.*

## Estado actual | Current Status

KMC se encuentra en desarrollo activo y cuenta con los siguientes componentes:

*KMC is in active development and includes the following components:*

- **Core parser**: Implementado en `kmc_parser/parser.py` *(Implemented in `kmc_parser/parser.py`)*
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
- **Integración con LlamaIndex** para búsqueda semántica y generación basada en conocimiento  
  *Integration with LlamaIndex for semantic search and knowledge-based generation*
- **Soporte para encadenamiento de variables** para workflows complejos  
  *Support for variable chaining for complex workflows*
- **Compatible con Markdown estándar** - funciona con todos los visualizadores de Markdown  
  *Compatible with standard Markdown - works with all Markdown viewers*
- **Definiciones integradas de variables** - sintaxis declarativa que relaciona variables de metadatos con fuentes generativas  
  *Integrated variable definitions - declarative syntax that relates metadata variables with generative sources*

## Arquitectura | Architecture

KMC consta de varios componentes:
*KMC consists of several components:*

1. **Parser KMC** (`kmc_parser/parser.py`): Núcleo que analiza y procesa documentos KMC  
   *KMC Parser (`kmc_parser/parser.py`): Core that analyzes and processes KMC documents*

2. **Handlers de Variables** (`kmc_parser/models.py`): Módulos para resolver diferentes tipos de variables  
   *Variable Handlers (`kmc_parser/models.py`): Modules for resolving different types of variables*
   ```python
   # kmc_parser/models.py
   class VariableHandler:
       def __init__(self, config):
           self.config = config
           self.handlers = {}

       def register_handler(self, handler_type: str, handler: callable):
           self.handlers[handler_type] = handler

       def resolve(self, var_type: str, var_name: str):
           handler = self.handlers.get(var_type)
           return handler(var_name) if handler else f"<{var_type}:{var_name}>"
   ```

3. **Integraciones** (`kmc_parser/integrations/`): Conectores para frameworks externos (LlamaIndex, etc.)  
   *Integrations (`kmc_parser/integrations/`): Connectors for external frameworks (LlamaIndex, etc.)*

4. **Sistema de Definición de Variables** (`kmc_parser/models.py:KMCVariableDefinition`): Implementa la sintaxis declarativa para relacionar variables  
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

```python
from kmc_parser import KMCParser
from kmc_parser.integrations import LlamaIndexHandler

# Crear el parser | Create the parser
parser = KMCParser()

# Registrar handlers para diferentes tipos de variables | Register handlers for different variable types
parser.register_context_handler("project", lambda var: "Proyecto Demo")
parser.register_metadata_handler("doc", lambda var: "v1.0")
parser.register_metadata_handler("kb", lambda var: "Esta es una cita importante de la base de conocimiento." if var == "cita1" else "")

# Registrar handler para variables generativas con LlamaIndex | Register handler for generative variables with LlamaIndex
llamaindex_handler = LlamaIndexHandler(index=my_index)
parser.register_generative_handler("ai:gpt4", llamaindex_handler)

# Renderizar un documento | Render a document
documento = """
# [[project:nombre]]
Versión: [{doc:version}]

## Resumen
{{ai:gpt4:resumen}}
<!-- AI_PROMPT FOR {{ai:gpt4:resumen}}: 
Genera un resumen conciso del proyecto a partir de [{kb:cita1}].
-->

<!-- KMC_DEFINITION FOR [{doc:conclusion}]:
GENERATIVE_SOURCE = {{ai:gpt4:conclusion}}
PROMPT = "Genera una conclusión para el proyecto basada en [{kb:cita1}]"
FORMAT = "markdown"
-->

## Conclusión
[{doc:conclusion}]
"""

resultado = parser.render(documento)
print(resultado)
```

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
- `quick_start/`: Ejemplos básicos para empezar a usar KMC:  
  *Basic examples to start using KMC:*
  - `kmc_example.py`: Ejemplo básico de uso programático  
    *Basic example of programmatic usage*
  - `markdown_kmc.md`: Plantilla de ejemplo usando la sintaxis KMC  
    *Example template using KMC syntax*

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

2. **Declarar los handlers e integraciones en Python**  
   *Declare handlers and integrations in Python*
   ```python
   from kmc_parser import KMCParser

   parser = KMCParser()

   # Registrar handlers | Register handlers
   parser.register_context_handler("project", lambda var: {
       "nombre": "Proyecto Demo",
       "tipo": "Análisis de mercado"
   }.get(var, f"<project:{var}>") )
   ```

3. **Procesar la plantilla**  
   *Process the template*
   ```python
   with open("plantilla.md", "r", encoding="utf-8") as f:
       contenido = f.read()

   resultado = parser.render(contenido)
   print(resultado)
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