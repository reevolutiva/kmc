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
        base_path = base_path or os.getcwd()
        stats = {"handlers": 0, "plugins": 0}

        for directory in self.EXTENSION_DIRECTORIES:
            full_path = os.path.join(base_path, directory)
            if os.path.exists(full_path):
                stats["handlers"] += self._scan_directory_for_handlers(full_path)
                stats["plugins"] += self._scan_directory_for_plugins(full_path)

        return stats
    
    def _scan_directory_for_handlers(self, directory):
        """Busca y registra handlers en un directorio"""
        self.logger.info(f"Escaneando handlers en: {directory}")
        handler_count = 0

        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(".py"):
                    module_name = os.path.splitext(file)[0]
                    module_path = os.path.join(root, file)
                    spec = importlib.util.spec_from_file_location(module_name, module_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if hasattr(attr, "__kmc_handler_type__") and hasattr(attr, "__kmc_var_type__"):
                            handler_type = getattr(attr, "__kmc_handler_type__")
                            var_type = getattr(attr, "__kmc_var_type__")

                            if handler_type == "context":
                                self.discovered_handlers.add((handler_type, var_type, attr))
                            elif handler_type == "metadata":
                                self.discovered_handlers.add((handler_type, var_type, attr))
                            elif handler_type == "generative":
                                self.discovered_handlers.add((handler_type, var_type, attr))

                            handler_count += 1

        return handler_count
    
    def _scan_directory_for_plugins(self, directory):
        """Busca y registra plugins en un directorio"""
        self.logger.info(f"Escaneando plugins en: {directory}")
        plugin_count = 0

        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(".py"):
                    module_name = os.path.splitext(file)[0]
                    module_path = os.path.join(root, file)
                    spec = importlib.util.spec_from_file_location(module_name, module_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if isinstance(attr, type) and issubclass(attr, KMCPlugin) and attr is not KMCPlugin:
                            self.discovered_plugins.add(attr)
                            plugin_count += 1

        return plugin_count
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
        discovery = ExtensionDiscovery()
        base_path = ext_directory or os.path.dirname(__file__)
        stats = discovery.discover_all_extensions(base_path=base_path)
        self.logger.info(f"Extensiones descubiertas: {stats}")
        
        # Registrar handlers descubiertos
        for handler_type, var_type, handler in discovery.discovered_handlers:
            if handler_type == "context":
                self.context_handlers[var_type] = handler()
            elif handler_type == "metadata":
                self.metadata_handlers[var_type] = handler()
            elif handler_type == "generative":
                self.generative_handlers[f"{var_type}"] = handler()
        
        # Registrar plugins descubiertos
        for plugin_cls in discovery.discovered_plugins:
            plugin_instance = plugin_cls()
            plugin_instance.initialize()
    
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
        if markdown_path is None and markdown_content is None:
            raise ValueError("Debe proporcionar markdown_path o markdown_content")
            
        # Cargar contenido del markdown
        if markdown_path:
            with open(markdown_path, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            content = markdown_content
            
        # Registrar handlers automáticamente
        self.auto_register_handlers(markdown_content=content, default_handlers=default_handlers)
        
        # Renderizar el documento
        return self.render(content)
    
    # Mantener los métodos existentes por compatibilidad
    def auto_register_handlers(self, markdown_path=None, markdown_content=None, default_handlers=None):
        """
        OBSOLETO: Use process_document en su lugar.
        Este método se mantiene por compatibilidad.
        """
        if markdown_path is None and markdown_content is None:
            raise ValueError("Debe proporcionar markdown_path o markdown_content")
            
        # Cargar contenido del markdown
        if markdown_path:
            with open(markdown_path, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            content = markdown_content
            
        # Configurar handlers predeterminados
        default_handlers = default_handlers or {
            "context": {},
            "metadata": {},
            "generative": {}
        }
        
        # Analizar el documento para identificar todas las variables
        doc = self.parse(content)
        
        # Estadísticas para el retorno
        stats = {
            "context": {},
            "metadata": {},
            "generative": {}
        }
        
        # Procesar variables contextuales
        for var in doc.contextual_vars:
            var_type = var.type
            
            # Si hay un handler predefinido para este tipo, lo usamos
            if var_type in default_handlers["context"]:
                self.context_handlers[var_type] = default_handlers["context"][var_type]
            elif var_type not in self.context_handlers: # Solo registrar si no existe ya uno
                # Primero, intentar obtener del registro centralizado
                registry_handler = registry.get_context_handler(var_type)
                if registry_handler:
                    self.context_handlers[var_type] = registry_handler
                else:
                    # Crear un handler genérico que devuelve un placeholder
                    self.context_handlers[var_type] = lambda var_name, vt=var_type: f"<{vt}:{var_name}>"
                
            # Registrar en estadísticas
            if var_type not in stats["context"]:
                stats["context"][var_type] = 0
            stats["context"][var_type] += 1
            
        # Procesar variables de metadata
        for var in doc.metadata_vars:
            var_type = var.type
            
            # Si hay un handler predefinido para este tipo, lo usamos
            if var_type in default_handlers["metadata"]:
                self.metadata_handlers[var_type] = default_handlers["metadata"][var_type]
            elif var_type not in self.metadata_handlers:
                # Primero, intentar obtener del registro centralizado
                registry_handler = registry.get_metadata_handler(var_type)
                if registry_handler:
                    self.metadata_handlers[var_type] = registry_handler
                else:
                    # Crear un handler genérico que devuelve un placeholder
                    self.metadata_handlers[var_type] = lambda var_name, vt=var_type: f"<{vt}:{var_name}>"
                
            # Registrar en estadísticas
            if var_type not in stats["metadata"]:
                stats["metadata"][var_type] = 0
            stats["metadata"][var_type] += 1
            
        # Procesar variables generativas
        for var in doc.generative_vars:
            handler_key = var.handler_key
            
            # Si hay un handler predefinido para este tipo, lo usamos
            if handler_key in default_handlers["generative"]:
                self.generative_handlers[handler_key] = default_handlers["generative"][handler_key]
            elif handler_key not in self.generative_handlers:
                # Primero, intentar obtener del registro centralizado
                registry_handler = registry.get_generative_handler(handler_key)
                if registry_handler:
                    self.generative_handlers[handler_key] = registry_handler
                else:
                    # Crear un handler genérico que genera un texto de placeholder
                    self.generative_handlers[handler_key] = lambda var_obj: f"<Contenido generativo para {var_obj.category}:{var_obj.subtype}:{var_obj.name}>"
                
            # Registrar en estadísticas
            if handler_key not in stats["generative"]:
                stats["generative"][handler_key] = 0
            stats["generative"][handler_key] += 1
            
        return stats
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
        base_path = base_path or os.getcwd()
        stats = {"handlers": 0, "plugins": 0}

        for directory in self.EXTENSION_DIRECTORIES:
            full_path = os.path.join(base_path, directory)
            if os.path.exists(full_path):
                stats["handlers"] += self._scan_directory_for_handlers(full_path)
                stats["plugins"] += self._scan_directory_for_plugins(full_path)

        return stats
        
    def _scan_directory_for_handlers(self, directory):
        """Searches for and registers handlers in a directory"""
        self.logger.info(f"Scanning handlers in: {directory}")
        handler_count = 0

        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(".py"):
                    module_name = os.path.splitext(file)[0]
                    module_path = os.path.join(root, file)
                    spec = importlib.util.spec_from_file_location(module_name, module_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if hasattr(attr, "__kmc_handler_type__") and hasattr(attr, "__kmc_var_type__"):
                            handler_type = getattr(attr, "__kmc_handler_type__")
                            var_type = getattr(attr, "__kmc_var_type__")

                            if handler_type == "context":
                                self.discovered_handlers.add((handler_type, var_type, attr))
                            elif handler_type == "metadata":
                                self.discovered_handlers.add((handler_type, var_type, attr))
                            elif handler_type == "generative":
                                self.discovered_handlers.add((handler_type, var_type, attr))

                            handler_count += 1

        return handler_count
        
    def _scan_directory_for_plugins(self, directory):
        """Searches for and registers plugins in a directory"""
        self.logger.info(f"Scanning plugins in: {directory}")
        plugin_count = 0

        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(".py"):
                    module_name = os.path.splitext(file)[0]
                    module_path = os.path.join(root, file)
                    spec = importlib.util.spec_from_file_location(module_name, module_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if isinstance(attr, type) and issubclass(attr, KMCPlugin) and attr is not KMCPlugin:
                            self.discovered_plugins.add(attr)
                            plugin_count += 1

        return plugin_count
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
        discovery = ExtensionDiscovery()
        base_path = ext_directory or os.path.dirname(__file__)
        stats = discovery.discover_all_extensions(base_path=base_path)
        self.logger.info(f"Discovered extensions: {stats}")
        
        # Register discovered handlers
        for handler_type, var_type, handler in discovery.discovered_handlers:
            if handler_type == "context":
                self.context_handlers[var_type] = handler()
            elif handler_type == "metadata":
                self.metadata_handlers[var_type] = handler()
            elif handler_type == "generative":
                self.generative_handlers[f"{var_type}"] = handler()
        
        # Register discovered plugins
        for plugin_cls in discovery.discovered_plugins:
            plugin_instance = plugin_cls()
            plugin_instance.initialize()
    
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
        if markdown_path is None and markdown_content is None:
            raise ValueError("Must provide markdown_path or markdown_content")
            
        # Load markdown content
        if markdown_path:
            with open(markdown_path, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            content = markdown_content
            
        # Automatically register handlers
        self.auto_register_handlers(markdown_content=content, default_handlers=default_handlers)
        
        # Render the document
        return self.render(content)
    
    # Keep existing methods for compatibility
    def auto_register_handlers(self, markdown_path=None, markdown_content=None, default_handlers=None):
        """
        DEPRECATED: Use process_document instead.
        This method is maintained for compatibility.
        """
        if markdown_path is None and markdown_content is None:
            raise ValueError("Must provide markdown_path or markdown_content")
            
        # Load markdown content
        if markdown_path:
            with open(markdown_path, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            content = markdown_content
            
        # Configure default handlers
        default_handlers = default_handlers or {
            "context": {},
            "metadata": {},
            "generative": {}
        }
        
        # Parse the document to identify all variables
        doc = self.parse(content)
        
        # Statistics for return
        stats = {
            "context": {},
            "metadata": {},
            "generative": {}
        }
        
        # Process contextual variables
        for var in doc.contextual_vars:
            var_type = var.type
            
            # If there is a predefined handler for this type, use it
            if var_type in default_handlers["context"]:
                self.context_handlers[var_type] = default_handlers["context"][var_type]
            elif var_type not in self.context_handlers: # Only register if one does not already exist
                # First, try to get from the centralized registry
                registry_handler = registry.get_context_handler(var_type)
                if registry_handler:
                    self.context_handlers[var_type] = registry_handler
                else:
                    # Create a generic handler that returns a placeholder
                    self.context_handlers[var_type] = lambda var_name, vt=var_type: f"<{vt}:{var_name}>"
                
            # Register in statistics
            if var_type not in stats["context"]:
                stats["context"][var_type] = 0
            stats["context"][var_type] += 1
            
        # Process metadata variables
        for var in doc.metadata_vars:
            var_type = var.type
            
            # If there is a predefined handler for this type, use it
            if var_type in default_handlers["metadata"]:
                self.metadata_handlers[var_type] = default_handlers["metadata"][var_type]
            elif var_type not in self.metadata_handlers:
                # First, try to get from the centralized registry
                registry_handler = registry.get_metadata_handler(var_type)
                if registry_handler:
                    self.metadata_handlers[var_type] = registry_handler
                else:
                    # Create a generic handler that returns a placeholder
                    self.metadata_handlers[var_type] = lambda var_name, vt=var_type: f"<{vt}:{var_name}>"
                
            # Register in statistics
            if var_type not in stats["metadata"]:
                stats["metadata"][var_type] = 0
            stats["metadata"][var_type] += 1
            
        # Process generative variables
        for var in doc.generative_vars:
            handler_key = var.handler_key
            
            # If there is a predefined handler for this type, use it
            if handler_key in default_handlers["generative"]:
                self.generative_handlers[handler_key] = default_handlers["generative"][handler_key]
            elif handler_key not in self.generative_handlers:
                # First, try to get from the centralized registry
                registry_handler = registry.get_generative_handler(handler_key)
                if registry_handler:
                    self.generative_handlers[handler_key] = registry_handler
                else:
                    # Create a generic handler that generates a placeholder text
                    self.generative_handlers[handler_key] = lambda var_obj: f"<Generative content for {var_obj.category}:{var_obj.subtype}:{var_obj.name}>"
                
            # Register in statistics
            if handler_key not in stats["generative"]:
                stats["generative"][handler_key] = 0
            stats["generative"][handler_key] += 1
            
        return stats
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
