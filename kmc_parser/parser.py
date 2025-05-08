"""
KMC Parser - Core parser para Kimfe Markdown Convention
"""
import re
from typing import Dict, List, Any, Callable, Optional, Union
import logging
from importlib import import_module
import os

from kmc_parser.models import ContextualVariable, MetadataVariable, GenerativeVariable, KMCDocument, KMCVariableDefinition
# Importar el sistema de registro centralizado
from kmc_parser.core import registry
from kmc_parser.extensions.auto_discovery import ExtensionDiscovery


class KMCParser:
    """Parser principal para documentos KMC"""
    
    def __init__(self, auto_discover=True, ext_directory=None):
        """
        Inicializa el parser KMC

        Args:
            auto_discover: Si debe descubrir automáticamente extensiones
            ext_directory: Directorio adicional donde buscar extensiones
        """
        self.context_handlers: Dict[str, Callable] = {}
        self.metadata_handlers: Dict[str, Callable] = {}
        self.generative_handlers: Dict[str, Callable] = {}
        self.variable_definitions: Dict[str, KMCVariableDefinition] = {}
        self.logger = logging.getLogger("kmc.parser")
        
        # Cargar extensiones automáticamente si está habilitado
        if auto_discover:
            self._auto_discover_extensions(ext_directory)

        # Intentar cargar plugins por defecto si existen
        try:
            self._load_default_plugins()
        except Exception as e:
            self.logger.debug(f"No se pudieron cargar plugins por defecto: {str(e)}")
    
    def _auto_discover_extensions(self, ext_directory=None):
        """Descubre y carga automáticamente extensiones del SDK"""
        discovery = ExtensionDiscovery()
        base_path = ext_directory or os.path.dirname(__file__)
        stats = discovery.discover_all_extensions(base_path=base_path)
        self.logger.info(f"Extensiones descubiertas: {stats}")
    
    def _load_default_plugins(self):
        """
        Carga plugins por defecto si están disponibles.
        Esta función intenta cargar plugins desde la carpeta kmc_parser/extensions
        si encuentra el módulo de plugin_manager.
        """
        from kmc_parser.extensions import plugin_manager
        
        # Intentar importar paquetes de plugins
        try:
            from kmc_parser import handlers
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
        2. Variables de metadata [{tipo:nombre}] - Solo se renderizan si tienen definición KMC_DEFINITION
        3. Variables generativas {{categoria:subtipo:nombre}} - Nunca se renderizan directamente

        Args:
            content (str): Contenido del documento KMC
        Returns:
            str: Documento con variables reemplazadas
        """
        doc = self.parse(content)
        result = content

        # Reemplazar variables contextuales
        for var in doc.contextual_vars:
            value = None
            
            # Intentar obtener un handler registrado para este tipo de variable
            registry_handler = registry.get_context_handler(var.type)
            
            if registry_handler:
                try:
                    value = registry_handler(var.name)
                except Exception as e:
                    self.logger.error(f"Error al resolver la variable contextual {var.type}:{var.name}: {str(e)}")
                    value = f"ERROR:{var.type}:{var.name}"
            
            # Si no hay handler en el registro, usar los handlers locales (compatibilidad hacia atrás)
            elif var.type in self.context_handlers:
                value = self.context_handlers[var.type](var.name)

            if value is not None:
                var.value = value
                result = result.replace(var.fullname, value)

        # Reemplazar variables de metadata SOLO si tienen definición KMC_DEFINITION
        for var in doc.metadata_vars:
            var_key = f"{var.type}:{var.name}"
            if var_key in self.variable_definitions:
                value = None
                
                # Intentar obtener un handler registrado para este tipo de variable
                registry_handler = registry.get_metadata_handler(var.type)
                
                if registry_handler:
                    try:
                        value = registry_handler(var.name)
                    except Exception as e:
                        self.logger.error(f"Error al resolver la variable de metadata {var.type}:{var.name}: {str(e)}")
                        value = f"ERROR:{var.type}:{var.name}"
                
                # Si no hay handler en el registro, usar los handlers locales (compatibilidad hacia atrás)
                elif var.type in self.metadata_handlers:
                    value = self.metadata_handlers[var.type](var.name)

                if value is not None:
                    var.value = value
                    result = result.replace(var.fullname, value)
            # Si no hay definición, dejar el placeholder intacto

        # NO reemplazar variables generativas directamente (cumple la convención)
        # for var in doc.generative_vars:
        #     ...

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
            handler_key = f"{var.category}:{var.subtype}"
            
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
                    self.generative_handlers[handler_key] = lambda name, prompt=None, format_type=None: \
                        f"<Contenido generativo para {var.category}:{var.subtype}:{name}>"
                
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
