from pydantic import BaseModel
from kmc_parser.extensions.lib.llamaindex import LlamaIndexMiddleware
from kmc_parser import (
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
    
    def make_template(self, options : MakeTemplateRequest ):
        """
        Create a template for KCM.
        """
        
        nombre = options.nombre
        descripcion = options.descripcion
        objetivo = options.objetivo
        instucciones = options.instucciones
        
        kmc_specs = ""
        
        prompt = f"""
        Genera una plantilla siguiendo las especificaciones KCM Documentation.
        
        {kmc_specs}
        
        Ahora te proporciono los detalles de la plantilla:
        Nombre: {nombre}
        Descripcion: {descripcion}
        Objetivo: {objetivo}
        Instrucciones: {instucciones}
        """
        
        llamaindexmiddleware = LlamaIndexMiddleware()
        llm_reponse = llamaindexmiddleware.agent_query(prompt)
        
        return llm_reponse
    
    def _generate_content(self, var):
        
        prompt = var.prompt
        print(f"var: {var}")
        
        promptParsed = {
            "nombre": "",
            "descripcion": "",
            "objetivo": "",
            "instucciones": ""  
        }
      
        
        options = MakeTemplateRequest(
            nombre=promptParsed["nombre"],
            descripcion=promptParsed["descripcion"],
            objetivo=promptParsed["objetivo"],
            instucciones=promptParsed["instucciones"]
        )
        
        content = self.make_template( options=options )
        
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

    