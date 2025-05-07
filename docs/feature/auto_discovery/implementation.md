# Implementación de Autodetección de Extensiones para KMC

_Fecha: 7 de mayo de 2025_

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