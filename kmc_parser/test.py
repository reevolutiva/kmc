from src.kmc.kmc_parser.extensions.template_maker.integrated_flow import KMC_Parser_TemplateMaker

parser = KMC_Parser_TemplateMaker(
    project_data={
        "nombre": "Curso de IA",
        "descripcion": "Curso de IA para principiantes",
        "objetivo": "Aprender los conceptos básicos de IA",
        "instucciones": "Sigue las instrucciones del curso"
    },
    doc_data={
        "version": "1.0.0",
        "titulo": "Demostración de Arquitectura Expandible",
    }
)


form_data = {
    "nombre": "Plantilla de IA",
    "descripcion": "Plantilla para crear documentos de IA",
    "objetivo": "Crear una plantilla para documentos de IA",
    "instucciones": "Sigue las instrucciones para crear la plantilla"
}

markdown = """

<!-- KMC_DEFINITION FOR [{tool:tempalte_maker_1}]:
    GENERATIVE_SOURCE = {{tool:tempalte_maker}}
    PROMPT = "Genera una planitilla en formato KMC con las siguientes caracteristicas: Nombre: Plantilla de IA. Descripcion: Plantilla para crear documentos de IA. Objetivo: Crear una plantilla para documentos de IA. Instrucciones: Sigue las instrucciones para crear la plantilla."
    FORMAT = "text/plain"
--> 

[{tool:tempalte_maker_1}]

"""

resultado = parser.parse(markdown)

print(resultado)