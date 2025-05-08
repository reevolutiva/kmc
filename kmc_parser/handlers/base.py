"""
Clases base para los handlers de variables en KMC.

Este módulo define las clases base para los diferentes tipos de handlers,
así como los decoradores que permiten su registro automático.
"""
import logging
from abc import ABC, abstractmethod
from functools import wraps
from typing import Optional, Callable, Any, Dict, Union

from ..core import registry


class BaseHandler(ABC):
    """Clase base abstracta para todos los handlers de variables KMC."""
    
    def __init__(self, context=None):
        """Inicializa el handler con configuración básica de logging y contexto opcional."""
        self.logger = logging.getLogger(f"kmc.handler.{self.__class__.__name__}")
        self.context = context or {}


class ContextHandler(BaseHandler):
    """Handler para variables contextuales [[tipo:nombre]]."""
    
    def __call__(self, var_name: str) -> str:
        """
        Método invocable que resuelve una variable contextual.
        
        Args:
            var_name: Nombre de la variable a resolver
            
        Returns:
            str: Valor resuelto para la variable
        """
        try:
            return self._get_context_value(var_name)
        except Exception as e:
            self.logger.error(f"Error al resolver variable contextual '{var_name}': {str(e)}")
            return f"ERROR:{var_name}"
    
    @abstractmethod
    def _get_context_value(self, var_name: str) -> str:
        """
        Método abstracto que cada subclase debe implementar para resolver variables.
        
        Args:
            var_name: Nombre de la variable a resolver
            
        Returns:
            str: Valor resuelto para la variable
        """
        pass


class MetadataHandler(BaseHandler):
    """Handler para variables de metadata [{tipo:nombre}]."""
    
    def __call__(self, var_name: str) -> str:
        """
        Método invocable que resuelve una variable de metadata.
        
        Args:
            var_name: Nombre de la variable a resolver
            
        Returns:
            str: Valor resuelto para la variable
        """
        try:
            return self._get_metadata_value(var_name)
        except Exception as e:
            self.logger.error(f"Error al resolver variable de metadata '{var_name}': {str(e)}")
            return f"ERROR:{var_name}"
    
    @abstractmethod
    def _get_metadata_value(self, var_name: str) -> str:
        """
        Método abstracto que cada subclase debe implementar para resolver variables.
        
        Args:
            var_name: Nombre de la variable a resolver
            
        Returns:
            str: Valor resuelto para la variable
        """
        pass


class GenerativeVariable:
    """Clase que representa una variable generativa con sus atributos."""
    
    def __init__(self, category: str, subtype: str, name: str = "", prompt: str = None, format_type: str = None, parameters: Dict[str, str] = None):
        """
        Inicializa una variable generativa.
        
        Args:
            category: Categoría de la variable (ej. "ai", "api", "tool")
            subtype: Subtipo dentro de la categoría (ej. "gpt4", "dalle", "weather")
            name: Nombre específico de la variable (opcional)
            prompt: Instrucción o prompt asociado a la variable
            format_type: Formato deseado para la salida
            parameters: Parámetros adicionales para la generación
        """
        self.category = category
        self.subtype = subtype
        self.name = name
        self.prompt = prompt
        self.format_type = format_type
        self.parameters = parameters or {}
        
    @property
    def fullname(self) -> str:
        """Devuelve el nombre completo de la variable en formato {{categoria:subtipo:nombre}}."""
        if self.name:
            return f"{{{{{self.category}:{self.subtype}:{self.name}}}}}"
        return f"{{{{{self.category}:{self.subtype}}}}}"
        
    @property
    def handler_key(self) -> str:
        """Devuelve la clave para buscar el handler (formato categoria:subtipo)."""
        return f"{self.category}:{self.subtype}"


class GenerativeHandler(BaseHandler):
    """Handler para variables generativas {{categoria:subtipo:nombre}}."""
    
    def __call__(self, name: str, prompt: str = None, format_type: str = None) -> str:
        """
        Método invocable que genera contenido para una variable generativa.
        
        Args:
            name: Nombre de la variable generativa
            prompt: Instrucción o prompt para la generación
            format_type: Formato deseado para la salida
            
        Returns:
            str: Contenido generado
        """
        try:
            var = GenerativeVariable(
                category=self.__kmc_var_type__.split(':')[0],
                subtype=self.__kmc_var_type__.split(':')[1],
                name=name,
                prompt=prompt,
                format_type=format_type
            )
            return self._generate_content(var)
        except Exception as e:
            self.logger.error(f"Error al generar contenido para '{name}': {str(e)}")
            return f"ERROR:{self.__kmc_var_type__}:{name}"
    
    @abstractmethod
    def _generate_content(self, var: GenerativeVariable) -> str:
        """
        Método abstracto que cada subclase debe implementar para generar contenido.
        
        Args:
            var: Variable generativa con todos sus atributos
            
        Returns:
            str: Contenido generado
        """
        pass


# Decoradores para registrar handlers automáticamente

def context_handler(var_type: str):
    """
    Decorador para registrar automáticamente handlers contextuales.
    
    Args:
        var_type: Tipo de variable contextual que este handler maneja
    """
    def decorator(cls):
        # Añadir metadatos a la clase para identificarla en autodiscovery
        setattr(cls, "__kmc_handler_type__", "context")
        setattr(cls, "__kmc_var_type__", var_type)
        
        # Registrar una instancia del handler si no es una clase abstracta
        if not getattr(cls, "__abstractmethod__", False):
            try:
                # Pasamos un contexto vacío por defecto
                handler_instance = cls({})
                registry.register_context_handler(var_type, handler_instance)
            except Exception as e:
                logger = logging.getLogger("kmc.handlers")
                logger.error(f"Error al registrar handler contextual para {var_type}: {str(e)}")
        
        return cls
    return decorator


def metadata_handler(var_type: str):
    """
    Decorador para registrar automáticamente handlers de metadata.
    
    Args:
        var_type: Tipo de variable de metadata que este handler maneja
    """
    def decorator(cls):
        # Añadir metadatos a la clase para identificarla en autodiscovery
        setattr(cls, "__kmc_handler_type__", "metadata")
        setattr(cls, "__kmc_var_type__", var_type)
        
        # Registrar una instancia del handler si no es una clase abstracta
        if not getattr(cls, "__abstractmethod__", False):
            try:
                # Pasamos un contexto vacío por defecto
                handler_instance = cls({})
                registry.register_metadata_handler(var_type, handler_instance)
            except Exception as e:
                logger = logging.getLogger("kmc.handlers")
                logger.error(f"Error al registrar handler de metadata para {var_type}: {str(e)}")
        
        return cls
    return decorator


def generative_handler(var_type: str):
    """
    Decorador para registrar automáticamente handlers generativos.
    
    Args:
        var_type: Tipo de variable generativa que este handler maneja (formato "categoria:subtipo")
    """
    def decorator(cls):
        # Verificar formato correcto
        if ":" not in var_type:
            logger = logging.getLogger("kmc.handlers")
            logger.error(f"Formato incorrecto para handler generativo: {var_type}. Debe ser 'categoria:subtipo'")
            return cls
        
        # Añadir metadatos a la clase para identificarla en autodiscovery
        setattr(cls, "__kmc_handler_type__", "generative")
        setattr(cls, "__kmc_var_type__", var_type)
        
        # Registrar una instancia del handler si no es una clase abstracta
        if not getattr(cls, "__abstractmethod__", False):
            try:
                # Pasamos un contexto vacío por defecto
                handler_instance = cls({})
                registry.register_generative_handler(var_type, handler_instance)
            except Exception as e:
                logger = logging.getLogger("kmc.handlers")
                logger.error(f"Error al registrar handler generativo para {var_type}: {str(e)}")
        
        return cls
    return decorator