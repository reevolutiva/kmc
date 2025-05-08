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

# Tutorial: Creación de Extensiones Autodetectables en KMC

Versión: 1.0
Fecha: 2025-05-07

Este tutorial te guiará a través del proceso de creación de tus propias extensiones (handlers y plugins) que pueden ser descubiertas y cargadas automáticamente por el KMC Parser.

## Prerrequisitos

*   Comprensión básica de Python y Clases.
*   KMC Parser instalado en tu entorno.
*   Familiaridad con la [Sintaxis KMC](../SYNTAX.md) y los [Conceptos de Autodetección](./auto_discovery.md).

## Parte 1: Creación de un Handler Contextual Autodetectable

Los Handlers Contextuales resuelven variables del tipo `[[tipo:nombre_variable]]`.

**Objetivo:** Crear un handler que resuelva `[[custom_user:nombre]]` y `[[custom_user:rol]]`.

1.  **Crea el archivo del Handler:**
    *   Dentro de tu proyecto, localiza o crea uno de los directorios de autodetección. Para este ejemplo, usaremos `user_extensions/`.
    *   Crea un nuevo archivo Python, por ejemplo: `user_extensions/my_custom_user_handler.py`.

2.  **Escribe el Código del Handler:**

    ```python
    # /ruta/a/tu/proyecto/user_extensions/my_custom_user_handler.py
    
    from kmc_parser.handlers.base import ContextHandler, context_handler
    
    @context_handler("custom_user") # Este decorador es clave para la autodetección
    class MyCustomUserHandler(ContextHandler):
        """Handler personalizado para obtener información del usuario."""
    
        def _get_context_value(self, var_name: str):
            """Resuelve el valor de la variable contextual."""
            if var_name == "nombre":
                return "Usuario Ejemplo"
            elif var_name == "rol":
                return "Desarrollador KMC"
            return None # Importante devolver None si la variable no se reconoce
    
    # No necesitas registrar nada manualmente aquí. 
    # El decorador @context_handler("custom_user") y la ubicación del archivo
    # en 'user_extensions/' son suficientes para que KMC lo encuentre.
    ```

3.  **Prueba tu Handler:**
    *   Crea un archivo Markdown de prueba (ej. `test.md`):
        ```markdown
        # Información del Usuario Personalizado
        
        Nombre: [[custom_user:nombre]]
        Rol: [[custom_user:rol]]
        Otro: [[custom_user:inexistente]] 
        ```
    *   Crea un script Python para procesarlo:
        ```python
        from kmc_parser import KMCParser
        import os
        
        # Asegúrate de que KMCParser pueda encontrar tu directorio de extensiones.
        # Si ejecutas este script desde la raíz de tu proyecto donde está 'user_extensions/',
        # KMC debería encontrarlo automáticamente.
        # Si no, podrías necesitar ajustar el PYTHONPATH o usar KMCParser(ext_directories=["ruta/a/user_extensions"])
        
        parser = KMCParser() # La autodetección está habilitada por defecto
        
        template_content = """
        # Información del Usuario Personalizado
        
        Nombre: [[custom_user:nombre]]
        Rol: [[custom_user:rol]]
        Otro: [[custom_user:inexistente]]
        """
        
        resultado = parser.process_document(template_content)
        print(resultado)
        ```
    *   Ejecuta el script. La salida esperada es:
        ```markdown
        # Información del Usuario Personalizado
        
        Nombre: Usuario Ejemplo
        Rol: Desarrollador KMC
        Otro: 
        ```
        (Nota: `[[custom_user:inexistente]]` se resuelve a una cadena vacía porque devolvimos `None`)

**¡Felicidades!** Has creado tu primer handler contextual autodetectable.

## Parte 2: Creación de un Handler Generativo Autodetectable

Los Handlers Generativos resuelven variables del tipo `{{categoria:subtipo:nombre_variable}}` y usualmente interactúan con sistemas externos o lógica compleja para generar contenido.

**Objetivo:** Crear un handler que simule una llamada a una API para `{{sim_api:weather:city_temperature}}`.

1.  **Crea el archivo del Handler:**
    *   Puedes usar el mismo directorio `user_extensions/` o, si prefieres, `custom_handlers/`.
    *   Crea un nuevo archivo Python, por ejemplo: `custom_handlers/simulated_api_handler.py`.

2.  **Escribe el Código del Handler:**

    ```python
    # /ruta/a/tu/proyecto/custom_handlers/simulated_api_handler.py
    
    from kmc_parser.handlers.base import GenerativeHandler, generative_handler
    from kmc_parser.models import GenerativeVariable # Necesario para type hinting
    
    @generative_handler("sim_api:weather") # Clave para autodetección
    class SimulatedWeatherApiHandler(GenerativeHandler):
        """Handler para simular llamadas a una API del clima."""
    
        def _generate_content(self, var: GenerativeVariable):
            """Genera contenido basado en la variable generativa."""
            # var.name sería 'city_temperature' en {{sim_api:weather:city_temperature}}
            # var.prompt contendría el prompt de KMC_DEFINITION si se usa.
            # Para este ejemplo simple, asumimos que el nombre de la variable es la ciudad.
            
            city = var.name # Asumimos que el nombre de la variable es la ciudad para este ejemplo
            # En un caso real, el prompt o los parámetros de la variable serían más útiles.
            
            if city == "london_temp":
                return "15°C"
            elif city == "newyork_temp":
                return "22°C"
            else:
                return f"Temperatura no disponible para {city}"
    ```

3.  **Prueba tu Handler:**
    *   Actualiza tu archivo Markdown de prueba (`test.md`) o crea uno nuevo:
        ```markdown
        # Clima Simulado
        
        Temperatura en Londres: {{sim_api:weather:london_temp}}
        Temperatura en Nueva York: {{sim_api:weather:newyork_temp}}
        Temperatura en París: {{sim_api:weather:paris_temp}}
        ```
    *   Usa un script Python similar al anterior:
        ```python
        from kmc_parser import KMCParser
        
        parser = KMCParser()
        
        template_content = """
        # Clima Simulado
        
        Temperatura en Londres: {{sim_api:weather:london_temp}}
        Temperatura en Nueva York: {{sim_api:weather:newyork_temp}}
        Temperatura en París: {{sim_api:weather:paris_temp}}
        """
        
        resultado = parser.process_document(template_content)
        print(resultado)
        ```
    *   Ejecuta el script. La salida esperada es:
        ```markdown
        # Clima Simulado
        
        Temperatura en Londres: 15°C
        Temperatura en Nueva York: 22°C
        Temperatura en París: Temperatura no disponible para paris_temp
        ```

## Parte 3: Creación de un Plugin Autodetectable

Los Plugins (`KMCPlugin`) son útiles para agrupar múltiples handlers, realizar configuraciones iniciales o registrar varios componentes a la vez.

**Objetivo:** Crear un plugin que registre un handler contextual para `[[my_plugin_info:version]]`.

1.  **Crea el archivo del Plugin:**
    *   Los plugins suelen ir en el directorio `plugins/`.
    *   Crea un nuevo archivo Python, por ejemplo: `plugins/my_info_plugin.py`.

2.  **Escribe el Código del Plugin y su Handler:**

    ```python
    # /ruta/a/tu/proyecto/plugins/my_info_plugin.py
    
    from kmc_parser.extensions.plugin_base import KMCPlugin
    from kmc_parser.core import registry # Necesario para registrar handlers desde el plugin
    from kmc_parser.handlers.base import ContextHandler 
    # No necesitas el decorador @context_handler aquí si registras desde el plugin
    
    # Primero, definimos el handler que el plugin registrará
    class PluginInfoHandler(ContextHandler):
        def _get_context_value(self, var_name: str):
            if var_name == "version":
                return "MyPlugin v1.0.0"
            return None
    
    # Ahora, definimos el Plugin
    # KMC buscará clases que hereden de KMCPlugin en esta carpeta.
    class MyInfoPlugin(KMCPlugin):
        """Un plugin de ejemplo que registra un handler de información."""
        
        def initialize(self):
            """Se llama cuando el plugin se carga. Aquí registramos nuestros handlers."""
            plugin_handler = PluginInfoHandler()
            # Usamos el registry directamente para registrar el handler
            registry.register_context_handler("my_plugin_info", plugin_handler)
            self.logger.info("MyInfoPlugin inicializado y handler registrado.") # Es buena práctica loguear
            return True # Es importante devolver True si la inicialización fue exitosa
        
        def cleanup(self):
            """Se llama si el plugin necesita liberar recursos (opcional)."""
            self.logger.info("MyInfoPlugin limpiado.")
            # Aquí podrías des-registrar el handler si fuera necesario, 
            # aunque no es común para la mayoría de los plugins.
    ```

3.  **Prueba tu Plugin:**
    *   Actualiza tu archivo Markdown de prueba (`test.md`):
        ```markdown
        # Información del Plugin
        
        Versión del Plugin: [[my_plugin_info:version]]
        ```
    *   Usa un script Python similar:
        ```python
        from kmc_parser import KMCParser
        
        # KMCParser descubrirá y cargará automáticamente MyInfoPlugin desde la carpeta 'plugins/'
        # y su método initialize() registrará el handler.
        parser = KMCParser()
        
        template_content = """
        # Información del Plugin
        
        Versión del Plugin: [[my_plugin_info:version]]
        """
        
        resultado = parser.process_document(template_content)
        print(resultado)
        ```
    *   Ejecuta el script. La salida esperada es:
        ```markdown
        # Información del Plugin
        
        Versión del Plugin: MyPlugin v1.0.0
        ```
        También deberías ver los mensajes de log de `MyInfoPlugin` en la consola si la configuración de logging de KMC lo permite.

## Conclusión

Has aprendido a crear diferentes tipos de extensiones autodetectables para KMC:

*   **Handlers Contextuales:** Usando el decorador `@context_handler` y colocando el archivo en un directorio de extensión.
*   **Handlers Generativos:** Usando el decorador `@generative_handler` de manera similar.
*   **Plugins:** Creando una clase que hereda de `KMCPlugin`, implementando `initialize()` para registrar handlers u otra lógica, y colocando el archivo en el directorio `plugins/`.

La clave para la autodetección es:

1.  **Ubicación del Archivo:** Colocar tus archivos Python en los directorios correctos (`extensions/`, `user_extensions/`, `custom_handlers/`, `plugins/`).
2.  **Decoradores (para Handlers):** Usar `@context_handler`, `@metadata_handler`, o `@generative_handler` para que KMC reconozca y registre tus handlers automáticamente cuando el módulo es importado.
3.  **Herencia (para Plugins):** Heredar de `KMCPlugin` para que KMC reconozca tu clase como un plugin.

Este sistema te permite mantener tu código de aplicación principal limpio y extender KMC de una manera modular y organizada.