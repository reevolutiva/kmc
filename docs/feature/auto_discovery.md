# Implementación de Autodetección de Extensiones para KMC
_Última actualización: 7 de mayo de 2025_

## Resumen Ejecutivo

La característica de autodetección de extensiones para KMC permitirá a los desarrolladores extender la funcionalidad del parser simplemente colocando sus archivos en directorios específicos, sin necesidad de modificar manualmente el código base o registrar explícitamente cada handler o plugin. Esto facilitará significativamente la creación de nuevas integraciones y reducirá la curva de aprendizaje para los nuevos desarrolladores.

## Motivación y Propósito

Actualmente, los desarrolladores que quieren extender KMC necesitan:
1. Crear clases que hereden de los handlers base
2. Registrar manualmente cada handler usando el sistema de registro
3. Modificar el código existente para cargar sus extensiones

La autodetección eliminará estos pasos manuales y permitirá una integración más fluida y modular.

## Componentes Principales de la Solución

### 1. Sistema de Descubrimiento de Extensiones (`ExtensionDiscovery`)

Se creará un componente central responsable de:
- Escanear directorios predefinidos en busca de extensiones
- Detectar clases que implementen las interfaces de handlers o plugins
- Registrar automáticamente los handlers y plugins encontrados
- Proporcionar información sobre las extensiones cargadas

Ubicación: `kmc_parser/extensions/auto_discovery.py`

### 2. Directorios Estandarizados

Se definirán varios directorios estándar para diferentes tipos de extensiones:
- `extensions/`: Extensiones propias del SDK
- `user_extensions/`: Extensiones creadas por usuarios
- `custom_handlers/`: Handlers personalizados
- `plugins/`: Plugins adicionales

### 3. Integración con KMCParser

Se modificará la clase `KMCParser` para:
- Incluir una opción de autodetección en el constructor
- Unificar los métodos `auto_register_handlers` y `render` en un solo método `process_document`
- Mantener compatibilidad con el código existente

### 4. Documentación y Ejemplos

Se proporcionará:
- Documentación detallada sobre cómo crear extensiones autodescubribles
- Ejemplos prácticos en `examples/expansible_architecture/`
- README.md actualizado para destacar esta nueva funcionalidad

## Arquitectura Detallada

### Clase ExtensionDiscovery

```python
class ExtensionDiscovery:
    """Descubre y carga automáticamente extensiones del SDK KMC"""
    
    EXTENSION_DIRECTORIES = [
        "extensions",        # Extensiones propias del SDK
        "user_extensions",   # Extensiones creadas por el usuario
        "custom_handlers",   # Handlers personalizados
        "plugins"            # Plugins adicionales
    ]
    
    def __init__(self):
        """Inicializa el sistema de descubrimiento"""
        self.logger = logging.getLogger("kmc.auto_discovery")
        self.discovered_handlers = set()
        self.discovered_plugins = set()
    
    def discover_all_extensions(self, base_path=None):
        """
        Descubre todas las extensiones disponibles en los directorios estándar
        
        Args:
            base_path: Ruta base donde buscar los directorios de extensiones
                       (por defecto es la raíz del paquete KMC)
        
        Returns:
            Diccionario con estadísticas de los elementos descubiertos
        """
        # Implementación...
        
    def _scan_directory_for_handlers(self, directory):
        """Busca y registra handlers en un directorio"""
        # Implementación...
        
    def _scan_directory_for_plugins(self, directory):
        """Busca y registra plugins en un directorio"""
        # Implementación...
```

### Actualización de KMCParser

```python
class KMCParser:
    def __init__(self, auto_discover=True, ext_directory=None):
        """
        Inicializa el parser KMC
        
        Args:
            auto_discover: Si debe descubrir automáticamente extensiones
            ext_directory: Directorio adicional donde buscar extensiones
        """
        self.context_handlers = {}
        self.metadata_handlers = {}
        self.generative_handlers = {}
        self.variable_definitions = {}
        
        # Cargar plugins y handlers automáticamente si está habilitado
        if auto_discover:
            self._auto_discover_extensions(ext_directory)
    
    def _auto_discover_extensions(self, ext_directory=None):
        """Descubre y carga automáticamente extensiones del SDK"""
        # Implementación...
    
    def process_document(self, markdown_path=None, markdown_content=None, default_handlers=None):
        """
        Método unificado para procesar un documento markdown en un solo paso.
        Este método combina auto_register_handlers y render, simplificando el flujo de trabajo.
        
        Args:
            markdown_path: Ruta al archivo markdown
            markdown_content: Contenido markdown directamente
            default_handlers: Handlers predefinidos
            
        Returns:
            Documento renderizado con todas las variables resueltas
        """
        # Implementación...
    
    # Mantener los métodos existentes por compatibilidad
    def auto_register_handlers(self, markdown_path=None, markdown_content=None, default_handlers=None):
        """
        OBSOLETO: Use process_document en su lugar.
        Este método se mantiene por compatibilidad.
        Se debe implementar una notificación para que el desarrollador deje de usarlo
        """
        # Implementación...
```

## Ejemplos de Uso

### Ejemplo Simple con Autodetección

```python
from kmc_parser import KMCParser

# Las extensiones se detectan automáticamente
parser = KMCParser()

# Procesar el documento en un solo paso
resultado = parser.process_document(markdown_path="plantilla.md")
print(resultado)
```

### Ejemplo con un Directorio de Extensiones Personalizado

```python
from kmc_parser import KMCParser

# Especificar un directorio adicional para extensiones
parser = KMCParser(ext_directory="/ruta/a/mis/extensiones")

# Procesar el documento
resultado = parser.process_document(markdown_path="plantilla.md")
print(resultado)
```

### Creación de una Extensión Personalizada

Archivo: `user_extensions/my_handler.py`
```python
from kmc_parser import context_handler, ContextHandler

@context_handler("cliente")
class ClienteHandler(ContextHandler):
    """Handler para variables contextuales [[cliente:nombre]]"""
    
    def _get_context_value(self, var_name):
        # Implementar lógica para obtener datos del cliente
        return f"Valor para cliente:{var_name}"
```

## Plan de Implementación

### Fase 1: Implementación Base
1. Crear la clase `ExtensionDiscovery` en `kmc_parser/extensions/auto_discovery.py`
2. Implementar las funciones de escaneo y registro

### Fase 2: Integración con KMCParser
1. Actualizar el constructor de `KMCParser` para usar autodetección
2. Crear el método unificado `process_document`
3. Mantener los métodos existentes por compatibilidad

### Fase 3: Estructura de Directorios
1. Crear los directorios estándar en el paquete KMC
2. Añadir README.md en cada directorio con instrucciones

### Fase 4: Documentación y Ejemplos
1. Actualizar el README.md principal con la nueva funcionalidad
2. Crear ejemplos prácticos en `examples/expansible_architecture/`
3. Actualizar la documentación existente

## Pruebas

Se deben crear pruebas para:
- Verificar que los handlers se detectan y registran correctamente
- Comprobar que los plugins se cargan adecuadamente
- Validar la compatibilidad con código existente
- Probar el funcionamiento con directorios personalizados

## Consideraciones y Limitaciones

- La autodetección podría aumentar ligeramente el tiempo de inicialización
- Se debe proporcionar un mecanismo para deshabilitar la autodetección si es necesario
- Los handlers y plugins autodescubiertos deben seguir una estructura específica

## Conclusiones

La implementación de autodetección de extensiones facilitará significativamente el proceso de extensión de KMC, permitiendo a los desarrolladores concentrarse en implementar su lógica específica sin preocuparse por la integración manual con el parser. Esta característica está alineada con la filosofía de KMC de ser un sistema modular, extensible y fácil de usar.

---

## English Version

# Auto-Discovery of Extensions Implementation for KMC
_Last update: May 7, 2025_

## Executive Summary

The auto-discovery of extensions feature for KMC will allow developers to extend the parser's functionality by simply placing their files in specific directories, without needing to manually modify the base code or explicitly register each handler or plugin. This will significantly facilitate the creation of new integrations and reduce the learning curve for new developers.

## Motivation and Purpose

Currently, developers who want to extend KMC need to:
1. Create classes that inherit from base handlers
2. Manually register each handler using the registry system
3. Modify existing code to load their extensions

Auto-discovery will eliminate these manual steps and allow for a more fluid and modular integration.

## Main Solution Components

### 1. Extension Discovery System (`ExtensionDiscovery`)

A central component will be created responsible for:
- Scanning predefined directories for extensions
- Detecting classes that implement handler or plugin interfaces
- Automatically registering found handlers and plugins
- Providing information about loaded extensions

Location: `kmc_parser/extensions/auto_discovery.py`

### 2. Standardized Directories

Several standard directories will be defined for different types of extensions:
- `extensions/`: SDK's own extensions
- `user_extensions/`: User-created extensions
- `custom_handlers/`: Custom handlers
- `plugins/`: Additional plugins

### 3. Integration with KMCParser

The `KMCParser` class will be modified to:
- Include an auto-discovery option in the constructor
- Unify the `auto_register_handlers` and `render` methods into a single `process_document` method
- Maintain compatibility with existing code

### 4. Documentation and Examples

The following will be provided:
- Detailed documentation on how to create self-discoverable extensions
- Practical examples in `examples/expansible_architecture/`
- Updated README.md to highlight this new functionality

## Detailed Architecture

### ExtensionDiscovery Class

```python
class ExtensionDiscovery:
    """Discovers and automatically loads KMC SDK extensions"""
    
    EXTENSION_DIRECTORIES = [
        "extensions",        # SDK's own extensions
        "user_extensions",   # User-created extensions
        "custom_handlers",   # Custom handlers
        "plugins"            # Additional plugins
    ]
    
    def __init__(self):
        """Initializes the discovery system"""
        self.logger = logging.getLogger("kmc.auto_discovery")
        self.discovered_handlers = set()
        self.discovered_plugins = set()
    
    def discover_all_extensions(self, base_path=None):
        """
        Discovers all available extensions in standard directories
        
        Args:
            base_path: Base path to search for extension directories
                       (by default is the KMC package root)
        
        Returns:
            Dictionary with statistics of discovered elements
        """
        # Implementation...
        
    def _scan_directory_for_handlers(self, directory):
        """Searches for and registers handlers in a directory"""
        # Implementation...
        
    def _scan_directory_for_plugins(self, directory):
        """Searches for and registers plugins in a directory"""
        # Implementation...
```

### KMCParser Update

```python
class KMCParser:
    def __init__(self, auto_discover=True, ext_directory=None):
        """
        Initializes the KMC parser
        
        Args:
            auto_discover: Whether to automatically discover extensions
            ext_directory: Additional directory to look for extensions
        """
        self.context_handlers = {}
        self.metadata_handlers = {}
        self.generative_handlers = {}
        self.variable_definitions = {}
        
        # Load plugins and handlers automatically if enabled
        if auto_discover:
            self._auto_discover_extensions(ext_directory)
    
    def _auto_discover_extensions(self, ext_directory=None):
        """Discovers and automatically loads SDK extensions"""
        # Implementation...
    
    def process_document(self, markdown_path=None, markdown_content=None, default_handlers=None):
        """
        Unified method to process a markdown document in one step.
        This method combines auto_register_handlers and render, simplifying the workflow.
        
        Args:
            markdown_path: Path to the markdown file
            markdown_content: Markdown content directly
            default_handlers: Predefined handlers
            
        Returns:
            Rendered document with all variables resolved
        """
        # Implementation...
    
    # Keep existing methods for compatibility
    def auto_register_handlers(self, markdown_path=None, markdown_content=None, default_handlers=None):
        """
        DEPRECATED: Use process_document instead.
        This method is maintained for compatibility.
        """
        # Implementation...
```

## Usage Examples

### Simple Example with Auto-Discovery

```python
from kmc_parser import KMCParser

# Extensions are automatically detected
parser = KMCParser()

# Process the document in one step
result = parser.process_document(markdown_path="template.md")
print(result)
```

### Example with a Custom Extensions Directory

```python
from kmc_parser import KMCParser

# Specify an additional directory for extensions
parser = KMCParser(ext_directory="/path/to/my/extensions")

# Process the document
result = parser.process_document(markdown_path="template.md")
print(result)
```

### Creating a Custom Extension

File: `user_extensions/my_handler.py`
```python
from kmc_parser import context_handler, ContextHandler

@context_handler("client")
class ClientHandler(ContextHandler):
    """Handler for contextual variables [[client:name]]"""
    
    def _get_context_value(self, var_name):
        # Implement logic to get client data
        return f"Value for client:{var_name}"
```

## Implementation Plan

### Phase 1: Base Implementation
1. Create the `ExtensionDiscovery` class in `kmc_parser/extensions/auto_discovery.py`
2. Implement scanning and registration functions

### Phase 2: Integration with KMCParser
1. Update the `KMCParser` constructor to use auto-discovery
2. Create the unified `process_document` method
3. Maintain existing methods for compatibility

### Phase 3: Directory Structure
1. Create standard directories in the KMC package
2. Add README.md in each directory with instructions

### Phase 4: Documentation and Examples
1. Update the main README.md with the new functionality
2. Create practical examples in `examples/expansible_architecture/`
3. Update existing documentation

## Testing

Tests should be created to:
- Verify that handlers are correctly detected and registered
- Check that plugins are properly loaded
- Validate compatibility with existing code
- Test functionality with custom directories

## Considerations and Limitations

- Auto-discovery might slightly increase initialization time
- A mechanism should be provided to disable auto-discovery if necessary
- Self-discovered handlers and plugins must follow a specific structure

## Conclusions

The implementation of extension auto-discovery will significantly facilitate the process of extending KMC, allowing developers to focus on implementing their specific logic without worrying about manual integration with the parser. This feature aligns with KMC's philosophy of being a modular, extensible, and easy-to-use system.