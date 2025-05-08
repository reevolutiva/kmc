"""
Clase base para plugins de KMC.

Este módulo define la clase base para todos los plugins de KMC,
estableciendo la interfaz común que deben implementar.
"""
import logging

class KMCPlugin:
    """
    Clase base para todos los plugins de KMC.
    
    Los plugins permiten extender la funcionalidad de KMC de manera modular,
    agrupando múltiples handlers u otras características bajo una interfaz común.
    """
    
    def __init__(self):
        """Inicializa el plugin con configuración básica y logging."""
        self.logger = logging.getLogger(f"kmc.plugin.{self.__class__.__name__}")
    
    def initialize(self):
        """
        Inicializa el plugin. Este método debe ser sobrescrito por las subclases.
        
        Típicamente, este método registra handlers u otros componentes en el sistema KMC.
        
        Returns:
            bool: True si la inicialización fue exitosa, False en caso contrario.
        """
        self.logger.warning(f"Método initialize() no implementado en {self.__class__.__name__}")
        return False
    
    def shutdown(self):
        """
        Finaliza el plugin limpiando recursos. Este método puede ser sobrescrito por las subclases.
        
        Se llama cuando el plugin se va a deshabilitar o cuando la aplicación se cierra.
        
        Returns:
            bool: True si la finalización fue exitosa, False en caso contrario.
        """
        return True