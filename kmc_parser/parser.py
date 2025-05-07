"""
KMC Parser - Core parser para Kimfe Markdown Convention
"""
import re
from typing import Dict, List, Any, Callable, Optional, Union
from .models import ContextualVariable, MetadataVariable, GenerativeVariable, KMCDocument, KMCVariableDefinition


class KMCParser:
    """Parser principal para documentos KMC"""
    
    def __init__(self):
        """Inicializa el parser KMC"""
        self.context_handlers: Dict[str, Callable] = {}
        self.metadata_handlers: Dict[str, Callable] = {}
        self.generative_handlers: Dict[str, Callable] = {}
        self.variable_definitions: Dict[str, KMCVariableDefinition] = {}
    
    def register_context_handler(self, var_type: str, handler: Callable) -> None:
        """Registra un handler para un tipo de variable contextual"""
        self.context_handlers[var_type] = handler
    
    def register_metadata_handler(self, var_type: str, handler: Callable) -> None:
        """Registra un handler para un tipo de variable de metadata"""
        self.metadata_handlers[var_type] = handler
    
    def register_generative_handler(self, var_type: str, handler: Callable) -> None:
        """Registra un handler para un tipo de variable generativa"""
        self.generative_handlers[var_type] = handler
    
    def _parse_contextual_vars(self, content: str) -> List[ContextualVariable]:
        """Extrae las variables contextuales del texto"""
        pattern = r'\[\[([\w]+):([\w_]+)\]\]'
        vars_found = []
        
        for match in re.finditer(pattern, content):
            var_type, var_name = match.groups()
            vars_found.append(ContextualVariable(var_type, var_name))
        
        return vars_found
    
    def _parse_metadata_vars(self, content: str) -> List[MetadataVariable]:
        """Extrae las variables de metadata del texto"""
        pattern = r'\[\{([\w]+):([\w_]+)\}\]'
        vars_found = []
        
        for match in re.finditer(pattern, content):
            var_type, var_name = match.groups()
            vars_found.append(MetadataVariable(var_type, var_name))
        
        return vars_found
    
    def _parse_generative_vars(self, content: str) -> List[GenerativeVariable]:
        """Extrae las variables generativas del texto"""
        pattern = r'\{\{([\w]+):([\w]+)(?::([\w_]+))?(?: ([^}]+))?\}\}'
        vars_found = []
        
        for match in re.finditer(pattern, content):
            category, subtype, name, params_str = match.groups()
            name = name or ""
            params = {}
            
            if params_str:
                # Procesar parámetros si existen
                for param in params_str.split():
                    if "=" in param:
                        key, value = param.split("=", 1)
                        params[key] = value
            
            vars_found.append(GenerativeVariable(category, subtype, name, parameters=params))
        
        return vars_found
    
    def _parse_prompts(self, content: str) -> Dict[str, str]:
        """Extrae los prompts asociados a variables generativas"""
        pattern = r'<!-- AI_PROMPT FOR (\{\{[\w:]+\}\}): (.*?) -->'
        prompts = {}
        
        for match in re.finditer(pattern, content, re.DOTALL):
            var_name, prompt = match.groups()
            prompts[var_name] = prompt.strip()
        
        return prompts
    
    def _parse_variable_definitions(self, content: str) -> Dict[str, KMCVariableDefinition]:
        """
        Extrae las definiciones de variables KMC del contenido
        
        Args:
            content (str): Contenido markdown completo
            
        Returns:
            Dict[str, KMCVariableDefinition]: Diccionario de definiciones indexado por nombre de variable
        """
        return KMCVariableDefinition.parse_definitions(content)
    
    def _resolve_contextual_var(self, var: ContextualVariable) -> Optional[str]:
        """Resuelve el valor de una variable contextual"""
        handler = self.context_handlers.get(var.type)
        if handler:
            return handler(var.name)
        return None
    
    def _resolve_metadata_var(self, var: MetadataVariable) -> Optional[str]:
        """Resuelve el valor de una variable de metadata"""
        # Primero, verificar si existe una definición para esta variable
        var_key = f"{var.type}:{var.name}"
        if var_key in self.variable_definitions:
            definition = self.variable_definitions[var_key]
            # Resolver la variable generativa asociada
            resolved_value = self._resolve_variable_definition(definition)
            if resolved_value is not None:
                return resolved_value
        
        # Si no hay definición o falló la resolución, usar el handler tradicional
        handler = self.metadata_handlers.get(var.type)
        if handler:
            return handler(var.name)
        return None
    
    def _resolve_generative_var(self, var: GenerativeVariable, doc: KMCDocument) -> Optional[str]:
        """
        Resuelve el valor de una variable generativa.
        
        Args:
            var (GenerativeVariable): La variable generativa a resolver
            doc (KMCDocument): El documento KMC completo
            
        Returns:
            Optional[str]: El valor generado o None si no se pudo resolver
        """
        # Obtener el handler correspondiente
        handler = self.generative_handlers.get(var.handler_key)
        if not handler:
            return None
        
        # Buscar el prompt asociado
        prompt = doc.prompts.get(var.fullname)
        if not prompt:
            return None
        
        # Resolver el prompt (reemplazar variables contextuales y de metadata)
        resolved_prompt = self._resolve_variables_in_text(prompt, doc)
        
        # Llamar al handler con el prompt resuelto
        var.prompt = resolved_prompt
        return handler(var)
    
    def _resolve_variable_definition(self, definition: KMCVariableDefinition) -> Optional[str]:
        """
        Resuelve una definición de variable KMC.
        
        Args:
            definition (KMCVariableDefinition): La definición a resolver
            
        Returns:
            Optional[str]: El valor generado o None si no se pudo resolver
        """
        # Obtener las partes de la variable generativa
        gen_parts = definition.generative_var.split(':')
        if len(gen_parts) < 2:
            return None
            
        category = gen_parts[0]
        subtype = gen_parts[1]
        name = gen_parts[2] if len(gen_parts) > 2 else ""
        
        # Crear la variable generativa
        gen_var = GenerativeVariable(category, subtype, name, prompt=definition.prompt)
        
        # Resolver el prompt (reemplazar variables)
        resolved_prompt = self._resolve_variables_in_prompt(definition.prompt)
        gen_var.prompt = resolved_prompt
        
        # Buscar el handler correspondiente
        handler_key = f"{category}:{subtype}"
        handler = self.generative_handlers.get(handler_key)
        if not handler:
            return None
            
        # Llamar al handler con la variable generativa
        return handler(gen_var)
    
    def _resolve_variables_in_text(self, text: str, doc: KMCDocument) -> str:
        """
        Resuelve todas las variables en un texto.
        
        Args:
            text (str): El texto con variables
            doc (KMCDocument): El documento KMC completo
            
        Returns:
            str: El texto con las variables resueltas
        """
        result = text
        
        # Resolver variables contextuales
        for var in doc.contextual_vars:
            if var.fullname in result:
                value = self._resolve_contextual_var(var)
                if value is not None:
                    result = result.replace(var.fullname, value)
        
        # Resolver variables de metadata
        for var in doc.metadata_vars:
            if var.fullname in result:
                value = self._resolve_metadata_var(var)
                if value is not None:
                    result = result.replace(var.fullname, value)
        
        return result
    
    def _resolve_variables_in_prompt(self, prompt: str) -> str:
        """
        Resuelve las variables en un prompt de definición.
        
        Args:
            prompt (str): El prompt con variables
            
        Returns:
            str: El prompt con variables resueltas
        """
        result = prompt
        
        # Resolver variables contextuales
        context_pattern = r'\[\[([\w]+):([\w_]+)\]\]'
        for match in re.finditer(context_pattern, prompt):
            var_type, var_name = match.groups()
            var = ContextualVariable(var_type, var_name)
            value = self._resolve_contextual_var(var)
            if value is not None:
                result = result.replace(var.fullname, value)
        
        # Resolver variables de metadata
        metadata_pattern = r'\[\{([\w]+):([\w_]+)\}\]'
        for match in re.finditer(metadata_pattern, prompt):
            var_type, var_name = match.groups()
            var = MetadataVariable(var_type, var_name)
            value = self._resolve_metadata_var(var)
            if value is not None:
                result = result.replace(var.fullname, value)
                
        return result
    
    def parse(self, content: str) -> KMCDocument:
        """
        Parsea un documento KMC y extrae todas las variables.
        
        Args:
            content (str): Contenido del documento KMC
            
        Returns:
            KMCDocument: Objeto con las variables extraídas
        """
        # Extraer variables y prompts
        contextual_vars = self._parse_contextual_vars(content)
        metadata_vars = self._parse_metadata_vars(content)
        generative_vars = self._parse_generative_vars(content)
        prompts = self._parse_prompts(content)
        
        # Extraer definiciones de variables
        self.variable_definitions = self._parse_variable_definitions(content)
        
        return KMCDocument(
            content=content,
            contextual_vars=contextual_vars,
            metadata_vars=metadata_vars,
            generative_vars=generative_vars,
            prompts=prompts
        )
    
    def render(self, content: str) -> str:
        """
        Renderiza un documento KMC reemplazando todas las variables por sus valores.
        
        Args:
            content (str): Contenido del documento KMC
            
        Returns:
            str: Documento con variables reemplazadas
        """
        doc = self.parse(content)
        result = content
        
        # Primero reemplazar las variables contextuales
        for var in doc.contextual_vars:
            value = self._resolve_contextual_var(var)
            if value is not None:
                var.value = value
                result = result.replace(var.fullname, value)
        
        # Luego reemplazar las variables de metadata
        for var in doc.metadata_vars:
            value = self._resolve_metadata_var(var)
            if value is not None:
                var.value = value
                result = result.replace(var.fullname, value)
        
        # Finalmente procesar las variables generativas
        for var in doc.generative_vars:
            value = self._resolve_generative_var(var, doc)
            if value is not None:
                var.value = value
                result = result.replace(var.fullname, value)
        
        # Eliminar comentarios de instrucciones
        result = re.sub(r'<!-- (AI_PROMPT|API_SOURCE|TOOL_CONFIG|CALC_FORMULA).+?-->', '', result, flags=re.DOTALL)
        
        # Eliminar comentarios de definiciones KMC
        result = re.sub(r'<!-- KMC_DEFINITION.+?-->', '', result, flags=re.DOTALL)
        
        return result