# Quick Start Example for KMC SDK
# Ejemplo de uso rápido del SDK KMC

This example shows how to use the KMC SDK to process Markdown templates with dynamic variables and AI prompts, following the KMC convention. It highlights the **auto-discovery** feature, which is the standard way to use KMC.

Este ejemplo muestra cómo utilizar el SDK de KMC para procesar plantillas Markdown con variables dinámicas y prompts de IA, siguiendo la convención KMC. Destaca la característica de **auto-descubrimiento**, que es la forma estándar de usar KMC.

## Included Files | Archivos incluidos

- `markdown_kmc.md`: Example template in Markdown format, with KMC variables and prompts.  
  *Plantilla de ejemplo en formato Markdown, con variables y prompts KMC.*
- `kmc_example.py`: Python script that loads the template and processes it using the KMC SDK. It relies on auto-discovery for handlers but can also use `default_handlers` for overrides or specific cases.  
  *Script Python que carga la plantilla y la procesa usando el SDK de KMC. Se basa en el auto-descubrimiento para los handlers, pero también puede usar `default_handlers` para anulaciones o casos específicos.*
- `auto_discovery_example.py`: Python script demonstrating the auto-discovery mechanism and how `default_handlers` can be used for custom behavior.  
  *Script Python que demuestra el mecanismo de auto-descubrimiento y cómo se pueden usar `default_handlers` para comportamiento personalizado.*

## What is KMC? | ¿Qué es KMC?

KMC (Kimfe Markdown Convention) is a convention for defining document templates with variables, metadata, and AI prompts, facilitating dynamic content generation and integration with language models. Its core philosophy is to simplify template creation and extension through an intuitive auto-discovery system for handlers and plugins.

KMC (Kimfe Markdown Convention) es una convención para definir plantillas de documentos con variables, metadatos y prompts de IA, facilitando la generación dinámica de contenido y la integración con modelos de lenguaje. Su filosofía central es simplificar la creación y extensión de plantillas a través de un sistema intuitivo de auto-descubrimiento para handlers y plugins.

## Template Structure | Estructura de la plantilla

The `markdown_kmc.md` template uses the following syntax:
*La plantilla `markdown_kmc.md` utiliza la siguiente sintaxis:*

- `[[context:variable]]`: Inserts the value of a context variable (e.g., `[[project:nombre]]`).  
  *Inserta el valor de una variable de contexto (por ejemplo, `[[project:nombre]]`).*
- `[{metadata:variable}]`: Inserts document metadata.  
  *Inserta metadatos del documento.*
- `{{ai:model:variable}}`: Defines a block for an AI model to generate dynamic content.  
  *Define un bloque para que un modelo de IA genere contenido dinámico.*
- AI prompts are defined in special HTML comments, for example:  
  *Los prompts para IA se definen en comentarios HTML especiales, por ejemplo:*
  ```html
  <!-- AI_PROMPT FOR {{ai:gpt4:resumen}}:
  Resume el objetivo principal del proyecto [[project:nombre]] para la organización [[org:nombre_empresa]].
  -->
  ```
- The new declarative syntax for linking metadata variables with generative sources:  
  *La nueva sintaxis declarativa para vincular variables de metadatos con fuentes generativas:*
  ```html
  <!-- KMC_DEFINITION FOR [{doc:conclusion}]:
  GENERATIVE_SOURCE = {{ai:gpt4:conclusion}}
  PROMPT = "Generate a conclusion for the project based on [{kb:cita1}]"
  FORMAT = "markdown"
  -->

  ## Conclusion
  [{doc:conclusion}]
  ```

## How the Example Works | ¿Cómo funciona el ejemplo?

1. **Template Definition | Definición de la plantilla:**
   - Edit `markdown_kmc.md` to customize variables and prompts according to your needs.  
     *Edita `markdown_kmc.md` para personalizar las variables y prompts según tus necesidades.*

2. **Handler/Plugin Creation (Optional) | Creación de Handlers/Plugins (Opcional):**
   - If you need custom logic for your variables, create handler or plugin files (e.g., `my_custom_handler.py`) and place them in the `user_extensions/`, `custom_handlers/`, or `plugins/` directories within your project. KMC will automatically detect and use them.  
     *Si necesitas lógica personalizada para tus variables, crea archivos de handler o plugin (ej. `mi_handler_personalizado.py`) y colócalos en los directorios `user_extensions/`, `custom_handlers/`, o `plugins/` dentro de tu proyecto. KMC los detectará y usará automáticamente.*

3. **Template Processing | Procesamiento de la plantilla:**
   - The `kmc_example.py` and `auto_discovery_example.py` scripts initialize `KMCParser()`. The parser automatically discovers and registers handlers from the standard extension directories.  
     *Los scripts `kmc_example.py` y `auto_discovery_example.py` inicializan `KMCParser()`. El parser descubre y registra automáticamente los handlers de los directorios de extensión estándar.*
   - The `process_document()` method is then called. It parses the template, resolves variables using the auto-discovered handlers (or provided `default_handlers`), and generates the final content.  
     *Luego se llama al método `process_document()`. Analiza la plantilla, resuelve las variables usando los handlers auto-descubiertos (o los `default_handlers` proporcionados), y genera el contenido final.*

4. **Execution | Ejecución:**
   - Run the scripts with:  
     *Ejecuta los scripts con:*
     ```bash
     python kmc_example.py
     python auto_discovery_example.py
     ```
   - The result is printed to the console, showing the processed template.  
     *El resultado se imprime por consola, mostrando la plantilla procesada.*

## Customization and Extension | Personalización y Extensión

- **Auto-Discovery is Key**: To add new variable types or custom logic, simply create a Python file with your handler class (decorated with `@context_handler`, `@metadata_handler`, or `@generative_handler`) and place it in an appropriate extension directory (e.g., `user_extensions/`). No manual registration in your main script is needed.  
  * **El Auto-Descubrimiento es Clave**: Para añadir nuevos tipos de variables o lógica personalizada, simplemente crea un archivo Python con tu clase de handler (decorada con `@context_handler`, `@metadata_handler`, o `@generative_handler`) y colócalo en un directorio de extensión apropiado (ej. `user_extensions/`). No se necesita registro manual en tu script principal.*
- **Override with `default_handlers`**: If needed, you can still pass a `default_handlers` dictionary to `process_document()` to provide specific handlers for certain variables, which will take precedence over auto-discovered ones for those specific variable types.  
  * **Sobrescribe con `default_handlers`**: Si es necesario, aún puedes pasar un diccionario `default_handlers` a `process_document()` para proporcionar handlers específicos para ciertas variables, los cuales tendrán precedencia sobre los auto-descubiertos para esos tipos de variables específicos.*
- Use the `KMC_DEFINITION` syntax for clearer and more maintainable templates.  
  *Utiliza la nueva sintaxis `KMC_DEFINITION` para plantillas más claras y mantenibles.*

## Advantages of KMC's Auto-Discovery | Ventajas del Auto-Descubrimiento de KMC

- **Simplicity**: Drastically reduces boilerplate. Just create your handlers and KMC finds them.  
  * **Simplicidad**: Reduce drásticamente el código repetitivo. Solo crea tus handlers y KMC los encuentra.*
- **Modularity**: Encourages organizing custom logic into separate, reusable handler/plugin files.  
  * **Modularidad**: Fomenta la organización de la lógica personalizada en archivos de handler/plugin separados y reutilizables.*
- **Extensibility**: Makes it easy to add or modify functionality without touching the core parsing logic or main application scripts.  
  * **Extensibilidad**: Facilita añadir o modificar funcionalidades sin tocar la lógica central del parser o los scripts principales de la aplicación.*
- **Maintainability**: Clear separation of concerns between template structure, content generation logic (handlers), and the KMC parser itself.  
  * **Mantenibilidad**: Clara separación de responsabilidades entre la estructura de la plantilla, la lógica de generación de contenido (handlers) y el propio parser KMC.*

---

For more information about the KMC convention and SDK, check the main project documentation or contact Reevolutiva.  
*Para más información sobre la convención KMC y el SDK, revisa la documentación principal del proyecto o contacta a Reevolutiva.*
