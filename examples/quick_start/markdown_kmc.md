# Ejemplo de plantilla Markdown usando KMC
# Example of Markdown template using KMC

# [[project:nombre]]
Versión | Version: [{doc:version}]
Organización | Organization: [[org:nombre_empresa]]

<!-- KMC_DEFINITION FOR [{doc:resumen_proyecto}]:
GENERATIVE_SOURCE = {{ai:gpt4:extract_summary}}
PROMPT = "Resume el objetivo principal del proyecto [[project:nombre]] para la organización [[org:nombre_empresa]]."
FORMAT = "text/markdown; max_length=200"
-->

## Resumen del Proyecto | Project Summary
[{doc:resumen_proyecto}]

## Detalles | Details
- Responsable | Responsible: [[user:nombre]]
- Fecha de inicio | Start date: [[project:fecha_inicio]]
- Estado | Status: [[project:estado]]

<!-- KMC_DEFINITION FOR [{doc:principales_objetivos}]:
GENERATIVE_SOURCE = {{ai:gpt4:objectives}}
PROMPT = "Genera una lista de 3-5 objetivos principales para el proyecto [[project:nombre]]"
FORMAT = "markdown; bullet_list"
-->

## Imagen del gion
[{image:imagen_gion}]
<!-- KMC_DEFINITION FOR [{image:imagen_gion}]:
GENERATIVE_SOURCE = {{ai:dalle:generation}}
PROMPT = "Genera una imagen representativa del proyecto [[project:nombre]]"
FORMAT = "image/png"
-->

## Objetivos | Objectives
[{doc:principales_objetivos}]

<!-- KMC_DEFINITION FOR [{doc:conclusiones}]:
GENERATIVE_SOURCE = {{ai:gpt4:conclusions}}
PROMPT = "Basado en el estado actual [[project:estado]] del proyecto, genera unas conclusiones preliminares"
FORMAT = "markdown; paragraph"
-->

## Conclusiones | Conclusions
[{doc:conclusiones}]
