"""
Base para plugins de extensión del KMC Parser
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import logging

from ..core.registry import registry


class KMCPlugin(ABC):
    """
    Clase base para todos los plugins de KMC.
    
    Los plugins permiten extender el KMC Parser con nuevas funcionalidades
    de forma modular y sin modificar el código base del sistema.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Inicializa un plugin con configuración opcional.
        
        Args:
            config: Configuración específica para el plugin
        """
        self.config = config or {}
        self.logger = logging.getLogger(f"kmc.plugin.{self.__class__.__name__}")
        self._registered = False
    
    @property
    def name(self) -> str:
        """Nombre identificador del plugin"""
        return self.__class__.__name__
    
    @property
    def version(self) -> str:
        """Versión del plugin"""
        return getattr(self.__class__, "__version__", "0.1.0")
    
    @property
    def description(self) -> str:
        """Descripción del plugin"""
        return self.__class__.__doc__ or "Sin descripción"
    
    @property
    def is_registered(self) -> bool:
        """Indica si el plugin ya está registrado"""
        return self._registered
    
    @abstractmethod
    def initialize(self) -> bool:
        """
        Inicializa el plugin y registra sus handlers y componentes.
        
        Returns:
            True si la inicialización fue exitosa, False en caso contrario
        """
        pass
    
    def register_handlers(self) -> int:
        """
        Registra los handlers proporcionados por este plugin.
        Debe ser implementado por clases derivadas que aporten handlers.
        
        Returns:
            Número de handlers registrados
        """
        return 0
    
    def cleanup(self) -> None:
        """
        Limpia recursos utilizados por el plugin.
        Este método debe ser llamado cuando el plugin ya no sea necesario.
        """
        pass
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Retorna metadatos del plugin.
        
        Returns:
            Diccionario con metadata del plugin
        """
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "config": {k: v for k, v in self.config.items() if k != "credentials"},
            "is_registered": self.is_registered
        }
    
    def __str__(self) -> str:
        """Representación en string del plugin"""
        return f"{self.name} v{self.version}"