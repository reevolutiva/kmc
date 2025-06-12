from kmc_parser.extensions.lib.llamaindex import ( llm, embed_model ) 
from kmc_parser import ( KMCParser,  plugin_manager,  registry )
from kmc_parser.extensions.template_maker.integrated_flow import KMC_Parser_TemplateMaker
from pydantic import BaseModel

def ai_generate_block( document_config : str, context :str, aikey : str , prompt: str, tag: str = False ):
    
    def print_prompt( raw_prompt : str ):
        
        system = (
            "Eres un asistente de IA que ayuda a crear un documento. "
            "Antes de crear el documento, debes analizar la siguiente información: "
            f"El nombre de la planitlla de documento es: {document_config['title']} "
            f"La descripcion de la plantilla de documento es: {document_config['descripcion']} "
            f"Informacion adicional: {document_config['ai_prompt']}"
        )

        comment = (
            "No ageres comentarios ni etiquetas HTML al resultado. "
            "Tampoco etiquetas de markdown. "
            "Solo devuelve el resultado en texto plano. "
            "Solo devuele lo que se te pide. "
            "No agregues nada más."
        )

        prompt = f"{system} {raw_prompt} {comment}"

        text = f'PROMPT = "{prompt}"'

        print("Generated Prompt:")
        print(text)

        return text
    
    prompt = """ <!-- KMC_DEFINITION FOR [{""" +  context + """}]:
    GENERATIVE_SOURCE = {{""" + aikey + """}}
    """ + print_prompt(prompt) + """
    FORMAT = "text/plain; max_length=80"
    --> 
    
    """
    
    if tag:
        prompt = prompt + f"""{tag} """ + """ [{"""+ context +"""}]"""
    else:
        prompt = prompt + """ [{"""+ context +"""}]"""

    
    return prompt

def kmc_dummy_md_generator( document_config ):
    
    from kmc_parser.extensions.plugin_llamaindex import LlamaIndexGenerativeHandler
    from kmc_parser.handlers.context.project import ProjectHandler
    
    resultado = ""
    
    parser = KMCParser()
    
    # Configurar y registrar el plugin de LlamaIndex
    llamaindex_plugin_config = {
        "query": "¿Cuál es la capital de Francia?"
    }
    
    project_config = {
        "project_data": {
         "nombre": "Curso de IA",   
        }
    }
    
    llamaindex_plugin = LlamaIndexGenerativeHandler( config=llamaindex_plugin_config)
    plugin_manager.register_plugin(llamaindex_plugin)
    registry.register_context_handler("project", ProjectHandler(config=project_config))
    
    
    parrafos = ai_generate_block( document_config=document_config, context="tool:llamaindexquery_parrs", aikey="tool:llamaindex", prompt="Crea 5 Parrafos del documento aleatorios, no añadas titulos solo los parrafos")
    
    temlpate = "# [[project:nombre]] \n"
    temlpate += f"""{parrafos}"""
    
    try:
        resultado = parser.process_document(markdown_content=temlpate)
        
        # Elimina espacios en blanco al principio y al final
        resultado = resultado.strip()
        # Elimina etiquetas HTML
        
    except Exception as e:
        print(f"Error generating markdown: {e}")
        resultado = "Error generating markdown"
        
    return resultado

class PromptData(BaseModel):
    nombre: str
    descripcion: str
    objetivo: str
    instruccion: str
    
def generate_prompt( prompt_data : PromptData ):

    def sanitize_text( txt :str ):
        # Reemplaza \n por <br/>
        txt = txt.replace("\n", "<br/>")

    nombre = sanitize_text(prompt_data.nombre)
    description = sanitize_text(prompt_data.descripcion)
    objetivo = sanitize_text(prompt_data.objetivo)
    instruccion = sanitize_text(prompt_data.instruccion)    
        
                
    
    prompt = f"""Genera una planitilla en formato KMC con las siguientes caracteristicas: Nombre: {nombre}. Descripcion: {description}. Objetivo: {objetivo}. Instrucciones: {instruccion}. """
    return prompt


def generate_kmc_template( prompt_data : PromptData ):
    """
    Generates a KMC-compliant Markdown template based on user-provided prompts.

    Args:
        prompt_data (dict): A dictionary containing the title, description, and AI prompt.

    Returns:
        str: The generated Markdown template.
    """
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

    <!-- KMC_DEFINITION FOR [{doc:tempalte_maker_1}]:
        GENERATIVE_SOURCE = {{tool:tempalte_maker}}
        PROMPT = " """ + generate_prompt(prompt_data) + """ "
        FORMAT = "text/plain"
    --> 

    [{doc:tempalte_maker_1}]

    """

    try:
        # Process the template
        result = parser.parse(markdown)
        return result
    except Exception as e:
        print(f"Error generating KMC template: {e}")
        return "Error generating template"
    
class KMC_PaserConfig(BaseModel):
    project_data: dict
    doc_data: dict  
     
def generate_document_kmc_parser( kmc_template : str, document_config : dict | KMC_PaserConfig ):
    
    from kmc_parser.extensions.plugin_llamaindex import LlamaIndexGenerativeHandler
    from kmc_parser.handlers.context.project import ProjectHandler
    
    resultado = ""
    
    parser = KMCParser()
    
    # Configurar y registrar el plugin de LlamaIndex
    llamaindex_plugin_config = {
        "query": "¿Cuál es la capital de Francia?"
    }
    
    project_config = {
        "project_data": {
          "nombre": "Curso de IA",   
        }
    }
    
    llamaindex_plugin = LlamaIndexGenerativeHandler( config=llamaindex_plugin_config)
    plugin_manager.register_plugin(llamaindex_plugin)
    registry.register_context_handler("project", ProjectHandler(config=project_config))
    
    
     
    parrafos = ai_generate_block( document_config=document_config, context="tool:llamaindex", aikey="tool:llamaindex", prompt="Crea 5 Parrafos del documento aleatorios, no añadas titulos solo los parrafos")
    
    temlpate = f"""{parrafos}"""
    
    kmc_template = kmc_template + temlpate
    
    print("KMC Template to process:")
    print(kmc_template)
    
    try:
        resultado = parser.process_document(markdown_content=kmc_template)
               
        return resultado

        
    except Exception as e:
        print(f"Error generating markdown: {e}")
        resultado = "Error generating markdown"
        return resultado
    
if __name__ == "__main__":
   
    kmc_template = """
        # KMC Template Example
        This is a basic KMC template for generating documents using AI.
        ## Instructions
        Use the AI to generate content based on the provided prompts.
    """
    document_config = {
        "title": "AI Document Template",
        "descripcion": "Template for creating AI documents",
        "ai_prompt": "Generate a KMC-compliant document template with the following characteristics: Name: AI Document Template. Description: Template for creating AI documents. Objective: Create a template for AI documents. Instructions: Follow the instructions to create the template."
    }
    
    kmc_template = generate_document_kmc_parser( kmc_template=kmc_template, document_config=document_config )
    print("Generated KMC Template:")
    print(kmc_template)