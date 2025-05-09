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

    def register_context_handler(self, context_type: str, handler: Callable) -> None:
        """Registra un handler para variables contextuales."""
        self.context_handlers[context_type] = handler

    def register_metadata_handler(self, metadata_type: str, handler: Callable) -> None:
        """Registra un handler para variables de metadatos."""
        self.metadata_handlers[metadata_type] = handler

    def register_generative_handler(self, source_type: str, handler: Callable) -> None:
        """Registra un handler para variables generativas."""
        self.generative_handlers[source_type] = handler
    
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
            
            print(f"Variable contextual encontrada: {var_type}:{var_name}")
        
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
        """
        Extrae variables generativas del contenido.
        """
        variables = []
        
        # Buscar variables generativas y sus definiciones o prompts
        var_pattern = r'{{([\w:]+)}}'
        for match in re.finditer(var_pattern, content):
            var_fullname = match.group(1)
            var_parts = var_fullname.split(':')
            
            # Extraer partes de la variable
            if len(var_parts) >= 2:
                category = var_parts[0]
                if len(var_parts) == 3:
                    subtype = var_parts[1]
                    name = var_parts[2]
                else:
                    subtype = None
                    name = var_parts[1]
                
                # Buscar definición KMC o prompt tradicional
                kmc_pattern = r'<!-- KMC {{' + re.escape(var_fullname) + r'}}:"([^"]+)"(?:\s*FORMAT\s+"([^"]+)")?\s*-->'
                ai_prompt_pattern = r'<!-- AI_PROMPT FOR {{' + re.escape(var_fullname) + r'}}:\s*\n(.*?)\n-->'
                
                prompt = None
                format_type = None
                
                # Primero intentar con definición KMC
                kmc_match = re.search(kmc_pattern, content, re.DOTALL)
                if kmc_match:
                    prompt = kmc_match.group(1)
                    format_type = kmc_match.group(2) if kmc_match.group(2) else None
                
                # Si no hay definición KMC, buscar prompt tradicional
                if not prompt:
                    ai_match = re.search(ai_prompt_pattern, content, re.DOTALL)
                    if ai_match:
                        prompt = ai_match.group(1).strip()
                
                # Crear la variable
                var = GenerativeVariable(
                    category=category,
                    subtype=subtype,
                    name=name,
                    prompt=prompt,
                    parameters={'format': format_type} if format_type else None
                )
                variables.append(var)
        
        return variables
    
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
        # handler = self.context_handlers.get(var.type)
        # if handler:
        #     print(f"Handler local encontrado para {var.type}. Hanlder: {handler} , Variable: {var.name}, {handler(var.name)}")
        #     return handler(var.name)
        
        # Si no hay handler local, buscar en el registro centralizado
        registry_handler = registry.get_context_handler(var.type)
        if registry_handler:
            print(f"Handler de registro encontrado para {var.type}")
            return registry_handler(var.name)
            
        return None
    
    def _resolve_metadata_var(self, var: MetadataVariable) -> str:
        """
        Resuelve el valor de una variable de metadata.
        """
        # Intentar con el handler local
        # handler = self.metadata_handlers.get(var.type)
        # if handler:
        #     value = handler(var.name)
        #     # Eliminar el prefijo 'v' si es una versión y ya está incluido
        #     if var.name == 'version' and str(value).startswith('v'):
        #         return str(value)[1:]
        #     return str(value)
        
        # Si no hay handler local, buscar en el registro centralizado
        registry_handler = registry.get_metadata_handler(var.type)
        if registry_handler:
            value = registry_handler(var.name)
            if var.name == 'version' and str(value).startswith('v'):
                return str(value)[1:]
            return str(value)
            
        # Si no hay handler, devolver un placeholder
        return f"<{var.type}:{var.name}>"
    
    def _resolve_generative_var(self, var: GenerativeVariable, doc: KMCDocument) -> str:
        """
        Resuelve el valor de una variable generativa.
        """
        # Obtener el handler correspondiente
        handler_key = var.handler_key
        handler = self.generative_handlers.get(handler_key)
        
        # Si no hay handler local, intentar obtener del registro
        if not handler:
            handler = registry.get_generative_handler(handler_key)
        
        if not handler:
            # Si no hay handler, devolver un placeholder
            return f"<Contenido generativo para {handler_key}>"

        # Buscar el prompt asociado
        prompt = var.prompt
        if not prompt:
            prompt = doc.prompts.get(var.fullname)
            
        if not prompt:
            # Si no hay prompt directo ni en las definiciones, usar un placeholder
            return f"<{var.handler_key}:{var.name}>"

        # Resolver el prompt (reemplazar variables contextuales y de metadata)
        resolved_prompt = self._resolve_variables_in_text(prompt, doc)
        var.prompt = resolved_prompt

        # Llamar al handler con el prompt resuelto
        try:
            format_type = var.parameters.get('format') if var.parameters else None
            if format_type:
                result = handler(var)
                if result is None:
                    return f"Contenido generado para {var.name} en formato {format_type}"
                return str(result)
            else:
                result = handler(var)
                if result is None:
                    return f"Contenido generado para {var.name}"
                return str(result)
        except Exception as e:
            self.logger.error(f"Error al ejecutar el handler para {var.fullname}: {str(e)}")
            return f"ERROR:{handler_key}:{var.name}"
    
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
        Analiza un documento KMC y extrae todas las variables y sus definiciones.
        """
        doc = KMCDocument(content=content)
        
        # Extraer variables contextuales
        doc.contextual_vars = self._parse_contextual_vars(content)
        
        # Extraer variables de metadata
        doc.metadata_vars = self._parse_metadata_vars(content)
        
        # Extraer variables generativas
        doc.generative_vars = self._parse_generative_vars(content)
        
        # Extraer definiciones KMC
        kmc_def_pattern = r'<!-- KMC_DEFINITION FOR \[{(.+?)}\]:\s*\n(.*?)-->'
        for match in re.finditer(kmc_def_pattern, content, re.DOTALL):
            var_name = match.group(1)
            definition_text = match.group(2)
            
            # Extraer propiedades de la definición
            source_match = re.search(r'GENERATIVE_SOURCE\s*=\s*{{(.+?)}}', definition_text)
            prompt_match = re.search(r'PROMPT\s*=\s*"(.+?)"', definition_text)
            format_match = re.search(r'FORMAT\s*=\s*"(.+?)"', definition_text)
            
            if source_match and prompt_match:
                # Asegurarnos de limpiar los espacios en blanco extras
                format_value = format_match.group(1).strip() if format_match else None
                
                definition = KMCVariableDefinition(
                    var_name=var_name.strip(),
                    source_var=source_match.group(1).strip(),
                    prompt=prompt_match.group(1).strip(),
                    format_type=format_value
                )
                doc.definitions[var_name] = definition
        
        # Extraer prompts tradicionales
        prompt_pattern = r'<!-- AI_PROMPT FOR {{(.+?)}}:\s*\n(.*?)-->'
        for match in re.finditer(prompt_pattern, content, re.DOTALL):
            var_name = match.group(1)
            prompt = match.group(2).strip()
            doc.prompts[var_name] = prompt
        
        return doc
    
    def render(self, content: str) -> str:
        """
        Renderiza un documento KMC, reemplazando todas las variables.
        """
        doc = self.parse(content)
        result = content

        # Limpiar comentarios de definición KMC
        result = re.sub(r'<!--\s*KMC_DEFINITION.+?-->\n?', '', result, flags=re.DOTALL)
        # Limpiar comentarios de AI_PROMPT
        result = re.sub(r'<!--\s*AI_PROMPT.+?-->\n?', '', result, flags=re.DOTALL)

        # Procesar definiciones KMC primero
        for var_name, definition in doc.definitions.items():
            # Extraer el handler de la fuente generativa
            source_parts = definition.source_var.split(':')
            if len(source_parts) < 2:
                continue
                
            handler_key = ':'.join(source_parts[:2]) if len(source_parts) > 2 else source_parts[0] + ':' + source_parts[1]
            handler = self.generative_handlers.get(handler_key)
            
            if not handler:
                handler = registry.get_generative_handler(handler_key)
            
            if handler:
                try:
                    # Resolver variables en el prompt
                    resolved_prompt = self._resolve_variables_in_text(definition.prompt, doc)
                    var_obj = GenerativeVariable(
                        category=source_parts[0],
                        subtype=source_parts[1],
                        name=source_parts[2] if len(source_parts) > 2 else var_name.split(':')[-1],
                        prompt=resolved_prompt,
                        parameters={'format': definition.format} if definition.format else None
                    )
                    
                    value = handler(var_obj)
                    if value is not None:
                        pattern = r'\[{' + re.escape(var_name) + r'}\]'
                        result = re.sub(pattern, str(value), result)
                    else:
                        pattern = r'\[{' + re.escape(var_name) + r'}\]'
                        result = re.sub(pattern, f"<{var_name}>", result)
                except Exception as e:
                    self.logger.error(f"Error al procesar definición {var_name}: {str(e)}")
                    pattern = r'\[{' + re.escape(var_name) + r'}\]'
                    result = re.sub(pattern, f"<{var_name}>", result)
            else:
                pattern = r'\[{' + re.escape(var_name) + r'}\]'
                result = re.sub(pattern, f"<{var_name}>", result)

        print("Comienza a procesar variables contextuales")
        # Procesar variables contextuales
        for var in doc.contextual_vars:
            value = self._resolve_contextual_var(var)
            print(f"Variable contextual: {var.fullname} -> {value}")
            if value:
                result = re.sub(r'\[\[' + re.escape(var.type) + r':' + re.escape(var.name) + r'\]\]', str(value), result)
            
        # Procesar variables de metadata
        for var in doc.metadata_vars:
            value = self._resolve_metadata_var(var)
            print(f"Variable de metadata: {var.fullname} -> {value}")
            if value:
                result = re.sub(r'\[{' + re.escape(var.type) + r':' + re.escape(var.name) + r'}\]', str(value), result)
        for var_name, definition in doc.definitions.items():
            # Extraer el handler de la fuente generativa
            source_parts = definition.source_var.split(':')
            if len(source_parts) < 2:
                continue
                
            handler_key = ':'.join(source_parts[:2]) if len(source_parts) > 2 else source_parts[0] + ':' + source_parts[1]
            handler = self.generative_handlers.get(handler_key)
            
            if not handler:
                handler = registry.get_generative_handler(handler_key)
            
            if handler:
                try:
                    # Resolver variables en el prompt
                    resolved_prompt = self._resolve_variables_in_text(definition.prompt, doc)
                    var_obj = GenerativeVariable(
                        category=source_parts[0],
                        subtype=source_parts[1],
                        name=source_parts[2] if len(source_parts) > 2 else var_name.split(':')[-1],
                        prompt=resolved_prompt,
                        parameters={'format': definition.format} if definition.format else None
                    )
                    
                    value = handler(var_obj)
                    if value is not None:
                        pattern = r'\[{' + re.escape(var_name) + r'}\]'
                        result = re.sub(pattern, str(value), result)
                    else:
                        pattern = r'\[{' + re.escape(var_name) + r'}\]'
                        result = re.sub(pattern, f"<{var_name}>", result)
                except Exception as e:
                    self.logger.error(f"Error al procesar definición {var_name}: {str(e)}")
                    pattern = r'\[{' + re.escape(var_name) + r'}\]'
                    result = re.sub(pattern, f"<{var_name}>", result)
            else:
                pattern = r'\[{' + re.escape(var_name) + r'}\]'
                result = re.sub(pattern, f"<{var_name}>", result)
        
        # Procesar las variables generativas restantes
        for var in doc.generative_vars:
            pattern = re.escape(var.fullname)
            if re.search(pattern, result): # Solo procesar si aún existe en el resultado
                handler_key = var.handler_key
                handler = self.generative_handlers.get(handler_key)
                
                if not handler:
                    handler = registry.get_generative_handler(handler_key)
                
                if handler:
                    try:
                        if var.prompt:
                            resolved_prompt = self._resolve_variables_in_text(var.prompt, doc)
                            var.prompt = resolved_prompt
                            
                        value = handler(var)
                        if value is not None:
                            result = re.sub(pattern, str(value), result)
                        else:
                            result = re.sub(pattern, f"<{handler_key}:{var.name}>", result)
                    except Exception as e:
                        self.logger.error(f"Error al procesar variable generativa {var.fullname}: {str(e)}")
                        result = re.sub(pattern, f"<{handler_key}:{var.name}>", result)
                else:
                    result = re.sub(pattern, f"<{handler_key}:{var.name}>", result)
        
        return result
    
    def auto_register_handlers(self, markdown_path: Optional[str] = None, 
                               markdown_content: Optional[str] = None,
                               default_handlers: Optional[Dict[str, Dict[str, Any]]] = None) -> Dict[str, Dict[str, int]]:
        """
        Registra automáticamente handlers para todas las variables encontradas en el documento.
        """
        # Obtener el contenido del documento
        content = ""
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
                # Crear un handler genérico que devuelve un placeholder
                self.context_handlers[var_type] = lambda var_name: f"<{var_type}:{var_name}>"
                
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
                # Crear un handler genérico que devuelve un placeholder
                self.metadata_handlers[var_type] = lambda var_name: f"<{var_type}:{var_name}>"
                
            # Registrar en estadísticas
            if var_type not in stats["metadata"]:
                stats["metadata"][var_type] = 0
            stats["metadata"][var_type] += 1
            
        # Procesar variables generativas
        for var in doc.generative_vars:
            handler_key = var.handler_key
            
            # Si hay un handler predefinido para esta clave, lo usamos
            if handler_key in default_handlers["generative"]:
                self.generative_handlers[handler_key] = default_handlers["generative"][handler_key]
            elif handler_key not in self.generative_handlers:
                # Crear un handler genérico que devuelve un placeholder
                self.generative_handlers[handler_key] = lambda var_obj: f"Contenido generado para {var_obj.name}"
            
            # Registrar en estadísticas
            if handler_key not in stats["generative"]:
                stats["generative"][handler_key] = 0
            stats["generative"][handler_key] += 1
            
        return stats
        
    def process_document(self, markdown_path: Optional[str] = None,
                          markdown_content: Optional[str] = None,
                          default_handlers: Optional[Dict[str, Dict[str, Any]]] = None) -> str:
        """
        Procesa un documento KMC completo, registrando handlers y renderizando el contenido.
        """
        # Obtener el contenido del documento
        content = ""
        if markdown_path:
            with open(markdown_path, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            content = markdown_content or ""
            
        # Auto-registrar handlers con los valores predeterminados
        self.auto_register_handlers(markdown_content=content, default_handlers=default_handlers)
        
        # Renderizar el documento
        return self.render(content)