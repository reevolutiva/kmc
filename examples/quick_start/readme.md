# Quick Start Example for KMC SDK
# Ejemplo de uso rápido del SDK KMC

This example shows how to use the KMC SDK to process Markdown templates with dynamic variables and AI prompts, following the KMC convention.

Este ejemplo muestra cómo utilizar el SDK de KMC para procesar plantillas Markdown con variables dinámicas y prompts de IA, siguiendo la convención KMC.

## Included Files | Archivos incluidos

- `markdown_kmc.md`: Example template in Markdown format, with KMC variables and prompts.  
  *Plantilla de ejemplo en formato Markdown, con variables y prompts KMC.*
- `kmc_example.py`: Python script that loads the template, registers context handlers, and processes the template using the KMC SDK.  
  *Script Python que carga la plantilla, registra handlers de contexto y procesa la plantilla usando el SDK de KMC.*

## What is KMC? | ¿Qué es KMC?

KMC (Kimfe Markdown Convention) is a convention for defining document templates with variables, metadata, and AI prompts, facilitating dynamic content generation and integration with language models.

KMC (Kimfe Markdown Convention) es una convención para definir plantillas de documentos con variables, metadatos y prompts de IA, facilitando la generación dinámica de contenido y la integración con modelos de lenguaje.

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

2. **Template Processing | Procesamiento de la plantilla:**
   - The `kmc_example.py` script loads the template and registers functions (handlers) to resolve each type of variable (`project`, `org`, `user`, `doc`).  
     *El script `kmc_example.py` carga la plantilla y registra funciones (handlers) para resolver cada tipo de variable (`project`, `org`, `user`, `doc`).*
   - The parser replaces variables with their values and prepares AI blocks to be processed by a language model.  
     *El parser reemplaza las variables por sus valores y deja los bloques de IA listos para ser procesados por un modelo de lenguaje.*

3. **Execution | Ejecución:**
   - Run the script with:  
     *Ejecuta el script con:*
     ```bash
     python kmc_example.py
     ```
   - The result is printed to the console, showing the processed template with example values.  
     *El resultado se imprime por consola, mostrando la plantilla procesada con los valores de ejemplo.*

## Customization | Personalización

- You can add more variables and handlers according to your project's requirements.  
  *Puedes agregar más variables y handlers según los requerimientos de tu proyecto.*
- Integrate your own AI model to process the `{{ai:model:variable}}` blocks.  
  *Integra tu propio modelo de IA para procesar los bloques `{{ai:model:variable}}`.*
- Use the new `KMC_DEFINITION` syntax for clearer and more maintainable templates.  
  *Utiliza la nueva sintaxis `KMC_DEFINITION` para plantillas más claras y mantenibles.*

## Advantages of KMC | Ventajas de KMC

- Standardizes the generation of dynamic documents.  
  *Estandariza la generación de documentos dinámicos.*
- Facilitates integration with AI and external systems.  
  *Facilita la integración con IA y sistemas externos.*
- Allows separation of data logic and document presentation.  
  *Permite separar la lógica de datos y la presentación del documento.*
- Declarative variable definitions improve traceability and maintainability.  
  *Las definiciones declarativas de variables mejoran la trazabilidad y mantenibilidad.*

---

For more information about the KMC convention and SDK, check the main project documentation or contact Reevolutiva.  
*Para más información sobre la convención KMC y el SDK, revisa la documentación principal del proyecto o contacta a Reevolutiva.*
