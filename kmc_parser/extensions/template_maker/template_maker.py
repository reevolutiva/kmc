from pydantic import BaseModel
from src.kmc.kmc_parser.extensions.lib.llamaindex import LlamaIndexMiddleware
import re
from src.kmc.kmc_parser import (
    registry, 
    GenerativeHandler,
    KMCPlugin
)

class MakeTemplateRequest( BaseModel ):
    nombre: str
    descripcion: str
    objetivo: str
    instucciones: str

class KMC_TemplateMaker(GenerativeHandler):
    
    __kmc_handler_type__ = "generative"
    __kmc_var_type__ = "tool:tempalte_maker"
    
    
    def llm_request( sefl, query: str, prompt_path : str, options : dict = None ):
        
        # Abrir docuemnto en ruta app/kmc/kmc_parser/prompts/kmc_template_constuctor.prompt.md
        print(" prompt_path: ", prompt_path)
        
        try:
            
            with open(prompt_path, "r") as f:
                prompt_content = f.read() 
                print("prompt config loaded successfully.")
        except Exception as e:
            print(f"Error: {e}")
            return None
        
        prompt = f"""
        {prompt_content}
        
        {query}
        """
        
        llamaindexmiddleware = LlamaIndexMiddleware()
        llm_reponse = llamaindexmiddleware.llm_query(prompt)
         
        return llm_reponse
    
    #def make_template(self, options : MakeTemplateRequest ):
    def make_template(self, query : str ):
        """
        Create a template for KCM.
        """
    
        kmc_specs_path = "/app/kmc/kmc_parser/prompts/kmc_template_constuctor.prompt.md"
        
        try:
            llm_reponse = self.llm_request(query=query, prompt_path=kmc_specs_path)
        except Exception as e:
            print(f"Error: {e}")
            return None
        
        return llm_reponse
    
    def revision_template(self, content: str):
        """
        Revisar el contenido de la plantilla generada.
        """
        
        kmc_specs_path = "/app/kmc/kmc_parser/prompts/kmc_template_reviewer.prompt.md"
        
        try:
            llm_reponse = self.llm_request(query=content, prompt_path=kmc_specs_path)
        except Exception as e:
            print(f"Error: {e}")
            return None
        
        return llm_reponse
    
    def _generate_content(self, var):
        
        prompt = var.prompt
        print(f"prompt: {prompt}")
        
        # Extract lines for Nombre, Descripcion, Objetivo, and Instrucciones using regex
        #matches = re.findall(r"^(Nombre|Descripcion|Objetivo|Instrucciones):\s*(.+?)(?:\.\s|$)", prompt, re.MULTILINE)
        
        #print(f"matches: {matches}")

        # Parse the matches into the promptParsed dictionary
        #promptParsed = {key.lower(): value.strip() for key, value in matches}
        
        #print(f"promptParsed: {promptParsed}")
        
        # promptParsed = {
        #     "nombre": "",
        #     "descripcion": "",
        #     "objetivo": "",
        #     "instucciones": ""  
        # }
      
        
        # options = MakeTemplateRequest(
        #     nombre=promptParsed["nombre"],
        #     descripcion=promptParsed["descripcion"],
        #     objetivo=promptParsed["objetivo"],
        #     instucciones=promptParsed["instucciones"]
        # )
        
        #content = self.make_template( options=options )
        first_parse = self.make_template( prompt )
        content = self.revision_template( first_parse )
        
        return content


class KMC_TemplateMakerPlugin(KMCPlugin):
    
    __version__ = "0.1.0"
    
    def __init__(self, genertative_key_string="tool:tempalte_maker"):
        """
        Inicializa el plugin de KMC Template Maker.
        
        Args:
            genertative_key_string (str): Clave generativa para el plugin.
        """
        super().__init__()
        self.genertative_key_string = genertative_key_string
        
    
    def initialize(self):
        """Inicializa el plugin."""
        self.logger.info(f"Inicializando {self.name} v{self.version}")
        self.register_handlers()
        return True
    
    def register_handlers(self):
        """Registra los handlers proporcionados por este plugin."""
       
       
        print("Registering KMC Template Maker")
        print(self.genertative_key_string)
       
        kmc_templatemaker = KMC_TemplateMaker() 
        registry.register_generative_handler( self.genertative_key_string, kmc_templatemaker )
        return 1

    