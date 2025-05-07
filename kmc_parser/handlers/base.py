"""
Base Handlers - Clases base para los handlers de variables KMC
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Callable, ClassVar, Type
from enum import Enum

from ..models import ContextualVariable, MetadataVariable, GenerativeVariable


class HandlerType(Enum):
    """Enumeración de los tipos de handlers disponibles"""
    CONTEXT = "context"
    METADATA = "metadata"
    GENERATIVE = "generative"


class BaseHandler(ABC):
    """Clase base para todos los handlers de variables KMC"""
    
    # Atributos de clase para registro automático
    __kmc_handler_type__: ClassVar[str] = None
    __kmc_var_type__: ClassVar[str] = None
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Inicializa el handler base.
        
        Args:
            config: Configuración opcional para el handler
        """
        self.config = config or {}
    
    @abstractmethod
    def handle(self, var_name: str) -> Any:
        """
        Método abstracto para procesar una variable.
        
        Args:
            var_name: Nombre de la variable a procesar
            
        Returns:
            Valor procesado
        """
        pass
    
    def __call__(self, var_name: str) -> Any:
        """
        Hace que los handlers sean callables directamente.
        
        Args:
            var_name: Nombre de la variable o la variable completa
            
        Returns:
            Valor procesado por el handler
        """
        return self.handle(var_name)


class ContextHandler(BaseHandler):
    """
    Clase base para handlers de variables contextuales [[tipo:nombre]].
    
    Los handlers de contexto procesan variables estáticas como información
    de proyecto, usuario, organización, etc.
    """
    
    __kmc_handler_type__ = HandlerType.CONTEXT.value
    
    def handle(self, var_name: str) -> Any:
        """
        Procesa una variable de contexto.
        
        Args:
            var_name: Nombre de la variable de contexto
            
        Returns:
            Valor de la variable contextual
        """
        if isinstance(var_name, ContextualVariable):
            var_name = var_name.name
        
        return self._get_context_value(var_name)
    
    @abstractmethod
    def _get_context_value(self, var_name: str) -> Any:
        """
        Método abstracto para obtener el valor de una variable contextual.
        
        Args:
            var_name: Nombre de la variable contextual
            
        Returns:
            Valor de la variable contextual
        """
        pass


class MetadataHandler(BaseHandler):
    """
    Clase base para handlers de variables de metadata [{tipo:nombre}].
    
    Los handlers de metadata procesan variables relacionadas con el documento
    o referencias a conocimiento externo.
    """
    
    __kmc_handler_type__ = HandlerType.METADATA.value
    
    def handle(self, var_name: str) -> Any:
        """
        Procesa una variable de metadata.
        
        Args:
            var_name: Nombre de la variable de metadata
            
        Returns:
            Valor de la variable de metadata
        """
        if isinstance(var_name, MetadataVariable):
            var_name = var_name.name
        
        return self._get_metadata_value(var_name)
    
    @abstractmethod
    def _get_metadata_value(self, var_name: str) -> Any:
        """
        Método abstracto para obtener el valor de una variable de metadata.
        
        Args:
            var_name: Nombre de la variable de metadata
            
        Returns:
            Valor de la variable de metadata
        """
        pass


class GenerativeHandler(BaseHandler):
    """
    Clase base para handlers de variables generativas {{categoria:subtipo:nombre}}.
    
    Los handlers generativos procesan variables que requieren generación dinámica
    de contenido usando LLMs, APIs externas, o herramientas.
    """
    
    __kmc_handler_type__ = HandlerType.GENERATIVE.value
    
    def handle(self, var: GenerativeVariable) -> Any:
        """
        Procesa una variable generativa.
        
        Args:
            var: Variable generativa a procesar
            
        Returns:
            Contenido generado
        """
        return self._generate_content(var)
    
    @abstractmethod
    def _generate_content(self, var: GenerativeVariable) -> Any:
        """
        Método abstracto para generar contenido dinámico.
        
        Args:
            var: Variable generativa con información de prompt, formato, etc.
            
        Returns:
            Contenido generado
        """
        pass


# Decoradores para facilitar el registro de handlers

def context_handler(var_type: str):
    """
    Decorador para registrar una clase como handler de variables contextuales.
    
    Args:
        var_type: Tipo de variable contextual (ej. "project", "user")
    """
    def decorator(cls):
        cls.__kmc_handler_type__ = HandlerType.CONTEXT.value
        cls.__kmc_var_type__ = var_type
        return cls
    return decorator


def metadata_handler(var_type: str):
    """
    Decorador para registrar una clase como handler de variables de metadata.
    
    Args:
        var_type: Tipo de variable de metadata (ej. "doc", "kb")
    """
    def decorator(cls):
        cls.__kmc_handler_type__ = HandlerType.METADATA.value
        cls.__kmc_var_type__ = var_type
        return cls
    return decorator


def generative_handler(var_type: str):
    """
    Decorador para registrar una clase como handler de variables generativas.
    
    Args:
        var_type: Tipo de variable generativa (ej. "ai:gpt4", "api:weather")
    """
    def decorator(cls):
        cls.__kmc_handler_type__ = HandlerType.GENERATIVE.value
        cls.__kmc_var_type__ = var_type
        return cls
    return decorator