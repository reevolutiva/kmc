"""
Modelos de datos para KMC Parser.

Este módulo define las estructuras de datos básicas utilizadas
por el parser KMC para representar variables y documentos.
"""
import re
from typing import List, Dict, Optional, Any

class KMCVariable:
    """Clase base para todas las variables KMC."""
    
    def __init__(self, var_type: str, name: str):
        """
        Inicializa una variable KMC.
        
        Args:
            var_type: Tipo de variable
            name: Nombre de la variable
        """
        self.type = var_type
        self.name = name
        self.value = None


class ContextualVariable(KMCVariable):
    """Representa una variable contextual [[tipo:nombre]]."""
    
    def __init__(self, var_type: str, name: str):
        """
        Inicializa una variable contextual.
        
        Args:
            var_type: Tipo de variable contextual (ej. "project", "user")
            name: Nombre específico de la variable
        """
        super().__init__(var_type, name)
    
    @property
    def fullname(self) -> str:
        """Devuelve el nombre completo de la variable en formato [[tipo:nombre]]."""
        return f"[[{self.type}:{self.name}]]"


class MetadataVariable(KMCVariable):
    """Representa una variable de metadata [{tipo:nombre}]."""
    
    def __init__(self, var_type: str, name: str):
        """
        Inicializa una variable de metadata.
        
        Args:
            var_type: Tipo de variable de metadata (ej. "doc", "kb")
            name: Nombre específico de la variable
        """
        super().__init__(var_type, name)
    
    @property
    def fullname(self) -> str:
        """Devuelve el nombre completo de la variable en formato [{tipo:nombre}]."""
        return f"[{{{self.type}:{self.name}}}]"


class GenerativeVariable(KMCVariable):
    """Representa una variable generativa {{categoria:subtipo:nombre}}."""
    
    def __init__(self, category: str, subtype: str, name: str = "", parameters: Dict[str, str] = None):
        """
        Inicializa una variable generativa.
        
        Args:
            category: Categoría de la variable (ej. "ai", "api", "tool")
            subtype: Subtipo dentro de la categoría (ej. "gpt4", "dalle", "weather")
            name: Nombre específico de la variable (opcional)
            parameters: Parámetros adicionales para la generación
        """
        super().__init__(f"{category}:{subtype}", name)
        self.category = category
        self.subtype = subtype
        self.parameters = parameters or {}
        self.prompt = None
        self.format_type = None
    
    @property
    def fullname(self) -> str:
        """Devuelve el nombre completo de la variable en formato {{categoria:subtipo:nombre}}."""
        if self.name:
            return f"{{{{{self.category}:{self.subtype}:{self.name}}}}}"
        return f"{{{{{self.category}:{self.subtype}}}}}"


class KMCVariableDefinition:
    """Representa una definición de variable KMC mediante KMC_DEFINITION."""
    
    def __init__(self, target_var: str, source_var: str, prompt: str = None, format_type: str = None):
        """
        Inicializa una definición de variable KMC.
        
        Args:
            target_var: Variable objetivo (ej. "{doc:resumen}")
            source_var: Variable generativa fuente (ej. "{{ai:gpt4:resumen}}")
            prompt: Instrucción o prompt para generar el contenido
            format_type: Formato deseado para la salida
        """
        self.target_var = target_var
        self.source_var = source_var
        self.prompt = prompt
        self.format_type = format_type
    
    @classmethod
    def parse_definitions(cls, content: str) -> Dict[str, 'KMCVariableDefinition']:
        """
        Extrae todas las definiciones de variables KMC_DEFINITION de un texto.
        
        Args:
            content: Texto markdown completo
            
        Returns:
            Dict: Diccionario de definiciones indexado por nombre de variable objetivo
        """
        pattern = r'<!-- KMC_DEFINITION FOR \[([\w]+):([\w_]+)\]:\s*' \
                 r'GENERATIVE_SOURCE\s*=\s*(\{\{[\w:]+(?::[\w_]+)?\}\})(?:\s*' \
                 r'PROMPT\s*=\s*"([^"]*)")?(?:\s*' \
                 r'FORMAT\s*=\s*"([^"]*)")?\s*-->'
        
        definitions = {}
        
        for match in re.finditer(pattern, content, re.DOTALL):
            var_type, var_name, source_var, prompt, format_type = match.groups()
            target_var = f"{var_type}:{var_name}"
            
            definition = cls(
                target_var=target_var,
                source_var=source_var,
                prompt=prompt,
                format_type=format_type
            )
            
            definitions[target_var] = definition
            
        return definitions


class KMCDocument:
    """Representa un documento KMC completo con sus variables extraídas."""
    
    def __init__(self, content: str, 
                 contextual_vars: List[ContextualVariable] = None,
                 metadata_vars: List[MetadataVariable] = None,
                 generative_vars: List[GenerativeVariable] = None,
                 prompts: Dict[str, str] = None):
        """
        Inicializa un documento KMC.
        
        Args:
            content: Contenido original del documento
            contextual_vars: Lista de variables contextuales
            metadata_vars: Lista de variables de metadata
            generative_vars: Lista de variables generativas
            prompts: Diccionario de prompts asociados a variables
        """
        self.content = content
        self.contextual_vars = contextual_vars or []
        self.metadata_vars = metadata_vars or []
        self.generative_vars = generative_vars or []
        self.prompts = prompts or {}
        
    def get_all_vars(self) -> List[KMCVariable]:
        """Devuelve una lista con todas las variables del documento."""
        return self.contextual_vars + self.metadata_vars + self.generative_vars