# Autodetección de Extensiones en KMC

Versión: 1.0
Fecha: 2025-05-07

## 1. Introducción

La característica de **Autodetección de Extensiones** es un pilar fundamental en la arquitectura de KMC (Kimfe Markdown Convention). Su objetivo principal es simplificar drásticamente la forma en que los desarrolladores extienden y personalizan el comportamiento del parser KMC. En lugar de requerir registros manuales de cada componente (como handlers o plugins) en el código principal de la aplicación, KMC puede descubrir y cargar automáticamente estas extensiones si se colocan en directorios predefinidos.

Este enfoque promueve:

*   **Modularidad:** Las extensiones se desarrollan como componentes independientes.
*   **Simplicidad:** Reduce el código boilerplate y la configuración manual.
*   **Extensibilidad:** Facilita la adición de nuevas funcionalidades sin modificar el núcleo del parser.
*   **Mantenibilidad:** Las extensiones son más fáciles de gestionar y actualizar.

## 2. ¿Cómo Funciona?

El mecanismo de autodetección se activa por defecto cuando se instancia `KMCParser`. El proceso general es el siguiente:

1.  **Escaneo de Directorios:** Al iniciarse, `KMCParser` (a través de su componente `ExtensionDiscovery`) escanea una serie de directorios estándar en busca de archivos Python. Estos directorios suelen incluir:
    *   `extensions/`: Para extensiones generales o proporcionadas por el propio KMC.
    *   `user_extensions/`: Destinado a extensiones personalizadas creadas por el usuario final de KMC.
    *   `custom_handlers/`: Específicamente para handlers de variables personalizados.
    *   `plugins/`: Para plugins más complejos que pueden agrupar múltiples handlers o funcionalidades.
    El parser también puede ser configurado para escanear directorios adicionales.

2.  **Identificación de Extensiones:** Dentro de los archivos Python encontrados, el sistema busca clases que:
    *   Implementen las interfaces base de KMC (ej. `ContextHandler`, `MetadataHandler`, `GenerativeHandler`, `KMCPlugin`).
    *   Estén decoradas con los decoradores de registro específicos (ej. `@context_handler("mi_tipo")`, `@generative_handler("mi_categoria:mi_subtipo")`).

3.  **Registro Automático:** Una vez identificadas, estas clases (handlers y plugins) se registran automáticamente en el `registry` central de KMC. Esto las hace disponibles para el parser durante el procesamiento de documentos Markdown.
    *   Los handlers se asocian con los tipos de variables que declaran manejar (ej. `[[mi_tipo:nombre_variable]]`).
    *   Los plugins ejecutan su lógica de inicialización, que típicamente incluye el registro de uno o más handlers.

4.  **Procesamiento del Documento:** Cuando se llama a `parser.process_document()`, el parser utiliza los handlers registrados (tanto los autodescubiertos como los que se puedan haber proporcionado explícitamente a través del argumento `default_handlers`) para resolver las variables KMC encontradas en el Markdown.

## 3. Componentes Clave

*   **`KMCParser` (`kmc_parser/parser.py`):** La clase principal que orquesta el parsing. Su constructor puede aceptar `auto_discover=True` (valor por defecto) y `ext_directories` (una lista de rutas a directorios adicionales para el descubrimiento).
*   **`ExtensionDiscovery` (`kmc_parser/extensions/auto_discovery.py`):** La clase responsable de la lógica de escaneo de directorios, importación de módulos y descubrimiento de clases de handlers/plugins.
*   **`Registry` (`kmc_parser/core/registry.py`):** El registro central donde todos los handlers (contextuales, de metadata, generativos) y plugins son almacenados y desde donde son recuperados por el parser.
*   **Decoradores de Handlers (ej. `@context_handler`, `@generative_handler` en `kmc_parser/handlers/base.py`):** Estos decoradores no solo marcan una clase como un handler, sino que también la registran automáticamente en el `registry` cuando el módulo que la contiene es importado durante el proceso de descubrimiento.
*   **Clases Base de Handlers y Plugins (ej. `ContextHandler`, `KMCPlugin`):** Las extensiones deben heredar de estas clases base para ser reconocidas y funcionar correctamente dentro del sistema KMC.

## 4. Ventajas del Enfoque de Autodetección

*   **Configuración Cero (Zero-Config) para Extensiones Básicas:** Los desarrolladores pueden añadir nueva lógica simplemente creando un archivo Python en el lugar correcto.
*   **Desarrollo Ágil:** Permite iterar rápidamente sobre nuevas extensiones sin necesidad de modificar código de inicialización central.
*   **Ecosistema de Extensiones:** Facilita la creación y compartición de extensiones KMC, ya que pueden ser "instaladas" simplemente copiando archivos.
*   **Código Más Limpio:** Las aplicaciones que utilizan KMC no necesitan estar llenas de código de registro manual para cada handler.
*   **Prioridad de `default_handlers`:** Aunque la autodetección es potente, KMC aún permite a los desarrolladores pasar un diccionario `default_handlers` al método `process_document()`. Estos handlers explícitos tienen prioridad sobre los autodescubiertos para los mismos tipos de variables, ofreciendo flexibilidad para casos específicos o para anular el comportamiento por defecto.

## 5. Casos de Uso Típicos

*   **Añadir un nuevo tipo de variable contextual:** Por ejemplo, `[[sistema:nombre_host]]` para obtener información del sistema. Se crearía un `SystemInfoHandler(ContextHandler)` en `user_extensions/`.
*   **Integrar una nueva API generativa:** Por ejemplo, para generar imágenes con un servicio específico `{{image:mi_servicio:prompt}}`. Se crearía un `MyImageServiceHandler(GenerativeHandler)` y se colocaría en `custom_handlers/` o dentro de un plugin en `plugins/`.
*   **Desarrollar un conjunto de herramientas para un dominio específico:** Agrupar varios handlers y lógica auxiliar en un `KMCPlugin` y colocarlo en `plugins/`.

## 6. Próximos Pasos

Para aprender cómo implementar tus propias extensiones autodetectables, consulta el siguiente tutorial:
*   [Tutorial: Creación de Extensiones Autodetectables en KMC](./auto_discovery/implementation.md)

## 7. Plan de Seguimiento a la Implementación

*Fecha de última actualización: 7 de mayo de 2025*

Para finalizar la implementación y lanzar esta funcionalidad como un repositorio abierto en GitHub, se ha establecido el siguiente plan de tareas pendientes:

### 7.1. Componentes Técnicos Pendientes

* **Tests Unitarios**:
  * Crear `tests/test_auto_discovery.py` con pruebas específicas para la autodetección
  * Incluir casos para diferentes directorios y estructuras de proyecto
  * Probar el manejo de errores con extensiones malformadas

* **Mejoras de Robustez**:
  * Mejorar el manejo de errores en `ExtensionDiscovery`
  * Implementar sistema de logging detallado para facilitar depuración
  * Garantizar compatibilidad entre diferentes sistemas operativos

### 7.2. Optimizaciones Propuestas

* **Caché de Descubrimiento**:
  * Implementar un sistema de caché para evitar re-escanear constantemente los directorios
  * Añadir detección de cambios para recargar solo cuando sea necesario

* **Lazy Loading**:
  * Modificar el sistema para cargar extensiones solo cuando se necesiten
  * Priorizar el rendimiento en proyectos con muchas extensiones

### 7.3. Documentación y Ejemplos

* **Ejemplos Avanzados**:
  * Expandir los ejemplos en `examples/expansible_architecture/`
  * Crear ejemplos de integración con frameworks populares

* **Diagramas y Visuales**:
  * Agregar diagramas de flujo del proceso de autodetección
  * Ilustrar la arquitectura de plugins y su integración

* **Plantillas y Buenas Prácticas**:
  * Crear plantillas para diferentes tipos de extensiones
  * Documentar patrones recomendados para crear extensiones eficientes

### 7.4. Preparación para GitHub

* **Repositorio Público**:
  * Configurar estructura de repositorio con archivos estándar (CONTRIBUTING.md, CODE_OF_CONDUCT.md)
  * Implementar GitHub Actions para CI/CD automático
  * Crear sistema de etiquetas para issues relacionados con extensiones

* **Comunidad**:
  * Establecer directrices para contribuciones de extensiones
  * Crear un índice/registro de extensiones de la comunidad

### 7.5. Cronograma Tentativo

* **Fase 1 (Componentes Técnicos)**: 1-2 semanas
* **Fase 2 (Documentación)**: 1 semana
* **Fase 3 (Preparación GitHub)**: 3-5 días
* **Fase 4 (Lanzamiento)**: 1 semana

**Fecha estimada de lanzamiento**: Finales de mayo 2025
