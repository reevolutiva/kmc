"""
Modelos de datos para el parser KMC
"""
from enum import Enum
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
import re


class VariableType(Enum):
    """Enumeración de tipos de variables KMC"""
    CONTEXTUAL = "contextual"  # Variables [[tipo:nombre]]
    METADATA = "metadata"      # Variables [{tipo:nombre}]
    GENERATIVE = "generative"  # Variables {{categoria:subtipo:nombre}}


@dataclass
class ContextualVariable:
    """Representa una variable contextual [[tipo:nombre]]"""
    type: str                  # Tipo de variable (project, user, org, etc.)
    name: str                  # Nombre de la variable
    value: Optional[str] = None  # Valor resuelto (si está disponible)
    
    @property
    def fullname(self) -> str:
        """Retorna el nombre completo de la variable con sintaxis KMC"""
        return f"[[{self.type}:{self.name}]]"


@dataclass
class MetadataVariable:
    """Representa una variable de metadata [{tipo:nombre}]"""
    type: str                  # Tipo de variable (doc, kb, ref, etc.)
    name: str                  # Nombre de la variable
    value: Optional[str] = None  # Valor resuelto (si está disponible)
    
    @property
    def fullname(self) -> str:
        """Retorna el nombre completo de la variable con sintaxis KMC"""
        return f"[{{{self.type}:{self.name}}}]"


@dataclass
class GenerativeVariable:
    """Representa una variable generativa {{categoria:subtipo:nombre}}"""
    category: str              # Categoría (ai, api, tool, etc.)
    subtype: Optional[str]     # Subtipo (gpt4, weather, sentiment, etc.)
    name: str                  # Nombre de la variable
    prompt: Optional[str] = None  # Prompt o instrucciones asociadas
    parameters: Dict[str, Any] = None  # Parámetros adicionales
    value: Optional[str] = None  # Valor resuelto (si está disponible)
    format: Optional[str] = None  # Formato deseado para la salida
    
    def __post_init__(self):
        """Inicializa valores por defecto"""
        if self.parameters is None:
            self.parameters = {}
    
    @property
    def fullname(self) -> str:
        """Retorna el nombre completo de la variable con sintaxis KMC"""
        if self.subtype:
            return f"{{{{{self.category}:{self.subtype}:{self.name}}}}}"
        else:
            return f"{{{{{self.category}:{self.name}}}}}"
    
    @property
    def handler_key(self) -> str:
        """Retorna la clave para buscar el handler correspondiente"""
        return f"{self.category}:{self.subtype}" if self.subtype else self.category


@dataclass
class KMCDocument:
    """Representa un documento KMC completo"""
    content: Optional[str] = None  # Contenido original del documento
    contextual_vars: List[ContextualVariable] = None  # Variables contextuales
    metadata_vars: List[MetadataVariable] = None      # Variables de metadata
    generative_vars: List[GenerativeVariable] = None  # Variables generativas
    prompts: Dict[str, str] = None  # Prompts asociados a variables
    definitions: Dict[str, 'KMCVariableDefinition'] = None  # Definiciones de variables

    def __post_init__(self):
        """Inicializa listas vacías para las variables"""
        if self.contextual_vars is None:
            self.contextual_vars = []
        if self.metadata_vars is None:
            self.metadata_vars = []
        if self.generative_vars is None:
            self.generative_vars = []
        if self.prompts is None:
            self.prompts = {}
        if self.definitions is None:
            self.definitions = {}
    
    @property
    def all_variables(self) -> Dict[str, List[Union[ContextualVariable, MetadataVariable, GenerativeVariable]]]:
        """Retorna todas las variables agrupadas por tipo"""
        return {
            VariableType.CONTEXTUAL.value: self.contextual_vars,
            VariableType.METADATA.value: self.metadata_vars,
            VariableType.GENERATIVE.value: self.generative_vars
        }


class KMCVariableDefinition:
    """
    Representa una definición integrada de variable que vincula una variable de metadata
    con una fuente generativa y sus instrucciones correspondientes.
    """
    
    def __init__(self, var_name: str, source_var: str, prompt: str, format_type: Optional[str] = None):
        """
        Inicializa una definición de variable KMC.
        
        Args:
            var_name (str): Nombre completo de la variable de metadata (ej: "doc:titulo_modulo")
            source_var (str): Nombre completo de la variable generativa (ej: "ai:gpt4:extract_title")
            prompt (str): Instrucción para generar el contenido
            format_type (str, optional): Formato deseado para la salida
        """
        self.var_name = var_name
        self.source_var = source_var
        self.prompt = prompt
        self.format_type = format_type
        self.dependencies = self._extract_dependencies()
        
        # Para compatibilidad con el código anterior
        self.metadata_var = var_name
        self.generative_var = source_var
        self.format = format_type

    def _extract_dependencies(self):
        """
        Extrae todas las variables referenciadas en el prompt.
        
        Returns:
            dict: Diccionario con las variables encontradas clasificadas por tipo
        """
        dependencies = {
            'context': [],  # Variables contextuales [[tipo:nombre]]
            'metadata': [],  # Variables de metadata [{tipo:nombre}]
            'generative': []  # Variables generativas {{categoria:subtipo:nombre}}
        }
        
        # Extraer variables contextuales [[tipo:nombre]]
        context_pattern = r'\[\[([\w]+):([\w_]+)\]\]'
        for match in re.finditer(context_pattern, self.prompt):
            var_type, var_name = match.groups()
            dependencies['context'].append(f"{var_type}:{var_name}")
            
        # Extraer variables de metadata [{tipo:nombre}]
        metadata_pattern = r'\[\{([\w]+):([\w_]+)\}\]'
        for match in re.finditer(metadata_pattern, self.prompt):
            var_type, var_name = match.groups()
            dependencies['metadata'].append(f"{var_type}:{var_name}")
            
        # Extraer variables generativas {{categoria:subtipo:nombre}}
        generative_pattern = r'\{\{([\w]+):([\w]+)(?::([\w_]+))?\}\}'
        for match in re.finditer(generative_pattern, self.prompt):
            category, subtype, name = match.groups()
            name = name or ''
            dependencies['generative'].append(f"{category}:{subtype}:{name}")
            
        return dependencies
    
    def to_dict(self):
        """
        Convierte la definición a un diccionario.
        
        Returns:
            dict: Representación en diccionario de la definición
        """
        return {
            'var_name': self.var_name,
            'source_var': self.source_var,
            'prompt': self.prompt,
            'format_type': self.format_type,
            'dependencies': self.dependencies
        }
    
    @classmethod
    def from_comment(cls, comment: str) -> Optional['KMCVariableDefinition']:
        """
        Crea una definición de variable desde un comentario KMC_DEFINITION.
        """
        pattern = r'KMC_DEFINITION FOR \[{(.+?)}\]:\s*\n' + \
                r'GENERATIVE_SOURCE\s*=\s*{{(.+?)}}\s*\n' + \
                r'PROMPT\s*=\s*"(.+?)"\s*\n' + \
                r'(?:FORMAT\s*=\s*"(.+?)"\s*)?'
        
        match = re.match(pattern, comment.strip(), re.DOTALL)
        if not match:
            return None
            
        var_name = match.group(1).strip()
        source_var = match.group(2).strip()
        prompt = match.group(3).strip()
        format_type = match.group(4).strip() if match.group(4) else None
        
        instance = cls(
            var_name=var_name,
            source_var=source_var,
            prompt=prompt,
            format_type=format_type
        )
        
        # For compatibility with old code
        instance.metadata_var = var_name
        instance.generative_var = source_var
        instance.format = format_type
        
        return instance
        
    @classmethod
    def parse_definitions(cls, content: str) -> Dict[str, 'KMCVariableDefinition']:
        """
        Extrae todas las definiciones KMC de un contenido markdown.
        
        Args:
            content (str): Contenido markdown completo
            
        Returns:
            dict: Diccionario de definiciones con la variable como clave
        """
        definitions = {}
        # Buscar comentarios de definición
        comment_pattern = r'<!--\s*(KMC_DEFINITION.+?)-->'
        comments = re.finditer(comment_pattern, content, re.DOTALL)
        
        for comment_match in comments:
            comment = comment_match.group(1)
            definition = cls.from_comment(comment)
            if definition:
                # Usar el nombre completo de la variable como clave
                definitions[definition.var_name] = definition
        
        return definitions