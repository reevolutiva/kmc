# Arquitectura Expandible de KMC Parser

> Última actualización: 2025-05-08

Esta carpeta contiene ejemplos y documentación para la arquitectura expandible del KMC Parser, que permite a los desarrolladores extender fácilmente las funcionalidades del parser sin modificar el código base.

## Bitácora de Cambios

- **2025-05-08:** Revisión y actualización completa del README.md para reflejar la estructura real de la carpeta y los ejemplos implementados en `demo.py`. Se añadieron descripciones detalladas de cada ejemplo, instrucciones de ejecución y recomendaciones de uso.
- **2025-05-07:** Versión inicial de la documentación de arquitectura expandible.

## Visión General

La arquitectura expandible del KMC Parser está diseñada para facilitar:

1. **Modularidad**: Separación clara de componentes y responsabilidades
2. **Extensibilidad**: Capacidad para añadir nuevas funcionalidades sin modificar el código existente
3. **Registro centralizado**: Sistema central para gestionar todos los handlers de variables
4. **Sistema de plugins**: Mecanismo para cargar/descargar dinámicamente funcionalidades
5. **Autodetección de extensiones**: Descubrimiento automático de handlers y plugins desde carpetas estándar

## Estructura de la Carpeta

- `demo.py`: Script principal de demostración con ejemplos de uso de la arquitectura expandible, handlers personalizados, plugins y autodetección.
- `README.md`: Este archivo de documentación.

## Ejemplos Incluidos en `demo.py`

El archivo `demo.py` contiene los siguientes ejemplos:

1. **Uso de Handlers Predefinidos**
   - Demuestra cómo registrar y utilizar handlers incluidos con el parser (ej. `ProjectHandler`, `DocumentMetadataHandler`, `GPT4Handler`).
2. **Creación de un Handler Personalizado**
   - Ejemplo de cómo definir y registrar un handler contextual propio usando decoradores.
3. **Uso del Sistema de Plugins**
   - Ejemplo de registro y uso de un plugin externo (`ExternalAPIsPlugin`) para integrar APIs de clima y mercado financiero.
4. **Creación de un Plugin Personalizado**
   - Ejemplo de cómo crear un plugin propio (`ToolsPlugin`) que agrupa y registra handlers utilitarios (ej. generación de eventos de calendario).
5. **Integración con LlamaIndex**
   - Demuestra cómo registrar y utilizar un plugin generativo externo para consultas avanzadas.

Para ejecutar la demostración:

```bash
python demo.py
```

Puedes descomentar los ejemplos que desees ejecutar en el bloque principal del script.

## Recomendaciones de Uso

- Utiliza decoradores (`@context_handler`, `@generative_handler`, etc.) para facilitar la autodetección y registro de tus handlers.
- Agrupa funcionalidades relacionadas en plugins para mantener una organización clara y facilitar la reutilización.
- Aprovecha la autodetección de extensiones colocando tus archivos en las carpetas estándar (`extensions/`, `user_extensions/`, `custom_handlers/`, `plugins/`).
- Consulta la documentación y los ejemplos en `docs/feature/auto_discovery.md` y `docs/feature/auto_discovery/implementation.md` para aprender a crear extensiones autodetectables.

## Recursos Relacionados

- [Documentación de Autodetección de Extensiones](../../docs/feature/auto_discovery.md)
- [Tutorial de Implementación de Extensiones](../../docs/feature/auto_discovery/implementation.md)
- [Ejemplo de Autodetección Rápida](../quick_start/auto_discovery_example.py)

## Notas

- Si agregas nuevos ejemplos o subcarpetas, actualiza este README.md y registra la fecha y el motivo del cambio en la bitácora.
- Si existen README.md en subcarpetas, actualízalos para reflejar los cambios relevantes, pero no crees nuevos README.md en subcarpetas si no existen.