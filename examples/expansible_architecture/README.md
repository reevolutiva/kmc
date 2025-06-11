# Arquitectura Expandible de KMC Parser

Esta carpeta contiene ejemplos y documentación para la arquitectura expandible del KMC Parser, que permite a los desarrolladores extender fácilmente las funcionalidades del parser sin modificar el código base.

## Visión General

La arquitectura expandible del KMC Parser está diseñada para facilitar:

1. **Modularidad**: Separación clara de componentes y responsabilidades
2. **Extensibilidad**: Capacidad para añadir nuevas funcionalidades sin modificar el código existente
3. **Registro centralizado**: Sistema central para gestionar todos los handlers de variables
4. **Sistema de plugins**: Mecanismo para cargar/descargar dinámicamente funcionalidades

## Componentes Principales

### 1. Registry (Registro Central)

El registro central (`registry`) es un punto único de acceso para todos los handlers de variables. Permite:

- Registrar y recuperar handlers para diferentes tipos de variables
- Cargar automáticamente handlers desde módulos
- Descubrir handlers en tiempo de ejecución

```python
from src.kmc.kmc_parser import registry, KMCParser

# Registrar un handler para variables de proyecto
registry.register_context_handler("project", mi_handler_proyecto)

# El parser utilizará automáticamente los handlers registrados
parser = KMCParser()
resultado = parser.render(contenido_markdown)
```

### 2. Base Handlers (Handlers Base)

Las clases base para todos los tipos de handlers:

- `BaseHandler`: Clase base abstracta para todos los handlers
- `ContextHandler`: Para variables contextuales `[[tipo:nombre]]`
- `MetadataHandler`: Para variables de metadata `[{tipo:nombre}]`
- `GenerativeHandler`: Para variables generativas `{{categoria:subtipo:nombre}}`

Estas clases implementan un patrón de diseño Template Method para facilitar la creación de handlers personalizados.

### 3. Sistema de Plugins

El sistema de plugins permite empaquetar múltiples handlers y funcionalidades relacionadas:

- `KMCPlugin`: Clase base para todos los plugins
- `plugin_manager`: Gestor de plugins para cargar/descargar plugins dinámicamente

```python
from src.kmc.kmc_parser import KMCPlugin, plugin_manager

class MiPlugin(KMCPlugin):
    def initialize(self):
        # Registrar handlers, configurar recursos, etc.
        return True

# Registrar el plugin
plugin_manager.register_plugin(MiPlugin())
```

## Cómo Extender KMC Parser

### 1. Crear un Handler Personalizado

```python
from src.kmc.kmc_parser import ContextHandler, context_handler

@context_handler("cliente")
class ClienteHandler(ContextHandler):
    """Handler para variables contextuales de cliente [[cliente:nombre]]"""
    
    def _get_context_value(self, var_name):
        # Implementar lógica para obtener datos del cliente
        # Por ejemplo, consultar una base de datos o API
        return f"Valor para cliente:{var_name}"
```

### 2. Crear un Handler Generativo

```python
from src.kmc.kmc_parser import GenerativeHandler, generative_handler
from src.kmc.kmc_parser.models import GenerativeVariable

@generative_handler("api:mysql")
class MySQLHandler(GenerativeHandler):
    """Handler para consultas MySQL {{api:mysql:consulta}}"""
    
    def __init__(self, config=None):
        super().__init__(config)
        # Configurar conexión a MySQL
        self.connection = None  # En producción: conectar a MySQL
    
    def _generate_content(self, var: GenerativeVariable):
        # Implementar lógica para ejecutar consultas SQL
        # y devolver resultados formateados
        query = var.prompt or "SELECT 'No query provided'"
        return f"Resultados de: {query}"
```

### 3. Crear un Plugin Completo

```python
from src.kmc.kmc_parser import KMCPlugin, registry
from src.kmc.kmc_parser.handlers.base import GenerativeHandler

class MiHandlerEspecializado(GenerativeHandler):
    # Implementación del handler...

class MiPlugin(KMCPlugin):
    """Plugin que añade funcionalidades especializadas"""
    __version__ = "1.0.0"
    
    def initialize(self):
        self.logger.info(f"Inicializando {self.name}")
        self.register_handlers()
        return True
    
    def register_handlers(self):
        mi_handler = MiHandlerEspecializado(config=self.config)
        registry.register_generative_handler("mi:tipo", mi_handler)
        return 1
    
    def cleanup(self):
        # Liberar recursos si es necesario
        pass
```

## Uso de la Arquitectura Expandible

El archivo `demo.py` en esta carpeta contiene ejemplos completos para:

1. Usar handlers predefinidos
2. Crear y usar handlers personalizados
3. Usar el sistema de plugins
4. Crear plugins personalizados

Para ejecutar la demostración:

```bash
python demo.py
```

## Integración con Aplicaciones Existentes

Para integrar la arquitectura expandible en una aplicación que ya usa KMC Parser:

1. Actualiza a la última versión del KMC Parser que incluye la arquitectura expandible
2. Registra tus handlers personalizados a través del sistema de registro central
3. Crea plugins para agrupar funcionalidades relacionadas

```python
from src.kmc.kmc_parser import KMCParser, registry

# Registrar handlers personalizados
registry.register_context_handler("mi_tipo", mi_handler)

# El parser utilizará automáticamente los handlers registrados
parser = KMCParser()
resultado = parser.process_document(markdown_path="documento.md")
```

## Consejos para Desarrolladores

1. **Usa decoradores** para definir tus handlers - simplifica el registro:
   ```python
   @context_handler("user")
   class UserHandler(ContextHandler):
       # Implementación...
   ```

2. **Agrupa funcionalidades relacionadas** en plugins para mantener una organización clara

3. **Aprovecha el sistema de auto-registro** para detectar automáticamente handlers y plugins disponibles

4. **Proporciona buena documentación** para tus handlers y plugins, especialmente sobre los tipos de variables que manejan

5. **Sigue el principio de responsabilidad única** - cada handler debe hacer una sola cosa y hacerla bien

## Ejemplos de Casos de Uso

- **Integración con APIs externas**: Crear handlers para obtener datos de APIs como WeatherAPI, Slack, GitHub, etc.
- **Conexiones a bases de datos**: Generar contenido a partir de consultas a bases de datos
- **Integraciones con IA**: Conectar con diferentes modelos de IA además de GPT-4
- **Herramientas especializadas**: Calculadoras, generadores de gráficos, formateadores, etc.
- **Variables contextuales personalizadas**: Información de empresa, equipos, proyectos específicos, etc.