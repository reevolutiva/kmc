"""
Plugin de ejemplo para pruebas de autodetección.

Este plugin es utilizado por las pruebas unitarias para verificar que el sistema de
autodetección funciona correctamente.
"""
from kmc_parser.extensions.plugin_base import KMCPlugin
from kmc_parser.core import registry

class TestPlugin(KMCPlugin):
    """Plugin de ejemplo para pruebas unitarias."""
    
    def initialize(self):
        """
        Inicializa el plugin registrando un handler de prueba.
        
        Returns:
            bool: True si la inicialización fue exitosa
        """
        self.logger.info("Inicializando TestPlugin para pruebas unitarias")
        
        # Registrar un handler contextual básico para pruebas
        registry.register_context_handler("test_plugin", 
                                         lambda var_name: f"Valor del plugin de prueba: {var_name}")
        
        return True
    
    def shutdown(self):
        """
        Finaliza el plugin.
        
        Returns:
            bool: True
        """
        self.logger.info("Cerrando TestPlugin")
        return True