"""
KMC Parser - Core parser para Kimfe Markdown Convention
"""
import re
from typing import Dict, List, Any, Callable, Optional, Union
import logging
from importlib import import_module

from .models import ContextualVariable, MetadataVariable, GenerativeVariable, KMCDocument, KMCVariableDefinition
# Importar el sistema de registro centralizado
from .core import registry


class KMCParser:
    """Parser principal para documentos KMC"""
    
    def __init__(self):
        """Inicializa el parser KMC"""
        self.context_handlers: Dict[str, Callable] = {}
        self.metadata_handlers: Dict[str, Callable] = {}
        self.generative_handlers: Dict[str, Callable] = {}
        self.variable_definitions: Dict[str, KMCVariableDefinition] = {}
        self.logger = logging.getLogger("kmc.parser")
        
        # Intentar cargar plugins por defecto si existen
        try:
            self._load_default_plugins()
        except Exception as e:
            self.logger.debug(f"No se pudieron cargar plugins por defecto: {str(e)}")
    
    def _load_default_plugins(self):
        """
        Carga plugins por defecto si están disponibles.
        Esta función intenta cargar plugins desde la carpeta kmc_parser/extensions
        si encuentra el módulo de plugin_manager.
        """
        from .extensions import plugin_manager
        
        # Intentar importar paquetes de plugins
        try:
            from . import handlers
            plugin_manager.load_discovered_plugins(handlers)
        except (ImportError, AttributeError) as e:
            self.logger.debug(f"No se pudieron cargar handlers automáticamente: {str(e)}")
    
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
        # Primero intentar con el handler local
        handler = self.context_handlers.get(var.type)
        if handler:
            return handler(var.name)
        
        # Si no hay handler local, buscar en el registro centralizado
        registry_handler = registry.get_context_handler(var.type)
        if registry_handler:
            return registry_handler(var.name)
            
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
        
        # Intentar con el handler local
        handler = self.metadata_handlers.get(var.type)
        if handler:
            return handler(var.name)
        
        # Si no hay handler local, buscar en el registro centralizado
        registry_handler = registry.get_metadata_handler(var.type)
        if registry_handler:
            return registry_handler(var.name)
            
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
        
        # Primero intentar con el handler local
        handler = self.generative_handlers.get(var.handler_key)
        
        # Si no hay handler local, buscar en el registro centralizado
        if not handler:
            handler = registry.get_generative_handler(var.handler_key)
            
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
        
        Reglas de renderizado:
        1. Variables contextuales [[tipo:nombre]] - Siempre se renderizan
        2. Variables de metadata [{tipo:nombre}] - Se renderizan cuando tienen definiciones o handlers
        3. Variables generativas {{categoria:subtipo:nombre}} - NUNCA se renderizan directamente,
           solo se utilizan como fuentes generativas en definiciones KMC_DEFINITION
        
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
        
        # Variables generativas NO se renderizan directamente en el texto final
        # Solo se utilizan como fuentes generativas en definiciones KMC_DEFINITION
        # Limpiamos las referencias a variables generativas del resultado
        for var in doc.generative_vars:
            # No reemplazamos la variable en el texto, su presencia es solo para referencia
            pass
        
        # Eliminar comentarios de instrucciones
        result = re.sub(r'<!-- (AI_PROMPT|API_SOURCE|TOOL_CONFIG|CALC_FORMULA).+?-->', '', result, flags=re.DOTALL)
        
        # Eliminar comentarios de definiciones KMC
        result = re.sub(r'<!-- KMC_DEFINITION.+?-->', '', result, flags=re.DOTALL)
        
        return result
    
    def auto_register_handlers(self, markdown_path=None, markdown_content=None, default_handlers=None):
        """
        Analiza un documento markdown y registra automáticamente los handlers necesarios
        para todas las variables encontradas. El registro se hace internamente.
        
        Esta función permite que el parser KMC automáticamente:
        1. Identifique todas las variables usadas en el documento (contextuales, metadata, generativas)
        2. Registre handlers genéricos para cada tipo identificado, si no se provee uno específico.
        3. Permita sobrescribir handlers específicos con el parámetro default_handlers.
        
        Args:
            markdown_path (str, optional): Ruta al archivo markdown.
            markdown_content (str, optional): Contenido markdown directamente.
            default_handlers (dict, optional): Diccionario con handlers predefinidos.
                Formato: {
                    "context": {"project": lambda var_name: "valor para " + var_name, ...},
                    "metadata": {"doc": lambda var_name: "valor para " + var_name, ...},
                    "generative": {"ai:gpt4": callable_handler, ...}
                }
        
        Returns:
            dict: Estadísticas de registro (tipos y número de variables registradas).
        """
        if markdown_path is None and markdown_content is None:
            raise ValueError("Debe proporcionar markdown_path o markdown_content")
            
        # Cargar contenido del markdown
        if markdown_path:
            with open(markdown_path, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            content = markdown_content
            
        # Configurar handlers predeterminados
        default_handlers = default_handlers or {
            "context": {},
            "metadata": {},
            "generative": {}
        }
        
        # Analizar el documento para identificar todas las variables
        doc = self.parse(content)
        
        # Estadísticas para el retorno
        stats = {
            "context": {},
            "metadata": {},
            "generative": {}
        }
        
        # Procesar variables contextuales
        for var in doc.contextual_vars:
            var_type = var.type
            
            # Si hay un handler predefinido para este tipo, lo usamos
            if var_type in default_handlers["context"]:
                self.context_handlers[var_type] = default_handlers["context"][var_type]
            elif var_type not in self.context_handlers: # Solo registrar si no existe ya uno
                # Primero, intentar obtener del registro centralizado
                registry_handler = registry.get_context_handler(var_type)
                if registry_handler:
                    self.context_handlers[var_type] = registry_handler
                else:
                    # Crear un handler genérico que devuelve un placeholder
                    self.context_handlers[var_type] = lambda var_name, vt=var_type: f"<{vt}:{var_name}>"
                
            # Registrar en estadísticas
            if var_type not in stats["context"]:
                stats["context"][var_type] = 0
            stats["context"][var_type] += 1
            
        # Procesar variables de metadata
        for var in doc.metadata_vars:
            var_type = var.type
            
            # Si hay un handler predefinido para este tipo, lo usamos
            if var_type in default_handlers["metadata"]:
                self.metadata_handlers[var_type] = default_handlers["metadata"][var_type]
            elif var_type not in self.metadata_handlers:
                # Primero, intentar obtener del registro centralizado
                registry_handler = registry.get_metadata_handler(var_type)
                if registry_handler:
                    self.metadata_handlers[var_type] = registry_handler
                else:
                    # Crear un handler genérico que devuelve un placeholder
                    self.metadata_handlers[var_type] = lambda var_name, vt=var_type: f"<{vt}:{var_name}>"
                
            # Registrar en estadísticas
            if var_type not in stats["metadata"]:
                stats["metadata"][var_type] = 0
            stats["metadata"][var_type] += 1
            
        # Procesar variables generativas
        for var in doc.generative_vars:
            handler_key = var.handler_key
            
            # Si hay un handler predefinido para este tipo, lo usamos
            if handler_key in default_handlers["generative"]:
                self.generative_handlers[handler_key] = default_handlers["generative"][handler_key]
            elif handler_key not in self.generative_handlers:
                # Primero, intentar obtener del registro centralizado
                registry_handler = registry.get_generative_handler(handler_key)
                if registry_handler:
                    self.generative_handlers[handler_key] = registry_handler
                else:
                    # Crear un handler genérico que genera un texto de placeholder
                    self.generative_handlers[handler_key] = lambda var_obj: f"<Contenido generativo para {var_obj.category}:{var_obj.subtype}:{var_obj.name}>"
                
            # Registrar en estadísticas
            if handler_key not in stats["generative"]:
                stats["generative"][handler_key] = 0
            stats["generative"][handler_key] += 1
            
        return stats
        
    def process_document(self, markdown_path=None, markdown_content=None, default_handlers=None):
        """
        Método simplificado para analizar y renderizar un documento markdown en un solo paso,
        registrando automáticamente los handlers necesarios.
        
        Esta función combina auto_register_handlers y render en una sola operación.
        
        Args:
            markdown_path (str, optional): Ruta al archivo markdown
            markdown_content (str, optional): Contenido markdown directamente
            default_handlers (dict, optional): Handlers predefinidos (ver auto_register_handlers)
            
        Returns:
            str: Documento renderizado con todas las variables resueltas
        """
        if markdown_path is None and markdown_content is None:
            raise ValueError("Debe proporcionar markdown_path o markdown_content")
            
        # Cargar contenido del markdown
        if markdown_path:
            with open(markdown_path, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            content = markdown_content
            
        # Registrar handlers automáticamente
        self.auto_register_handlers(markdown_content=content, default_handlers=default_handlers)
        
        # Renderizar el documento
        return self.render(content)