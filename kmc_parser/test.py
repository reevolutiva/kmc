from kmc_parser.extensions.template_maker.integrated_flow import KMC_Parser_TemplateMaker

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

markdown = """
# [[project:nombre]]
### [[project:descripcion]]


<!-- KMC_DEFINITION FOR [{tool:tempalte_maker}]:
    GENERATIVE_SOURCE = {{tool:tempalte_maker}}
    PROMPT = "NOMBRE:PROJECTO;DESCRIPCION:DESCRIPCION;OBJETIVO:OBJETIVO;INSTUCCIONES:INSTUCCIONES"
    FORMAT = "text/plain; max_length=80"
--> 

[{tool:tempalte_maker}]

"""

resultado = parser.parse(markdown)

print(resultado)