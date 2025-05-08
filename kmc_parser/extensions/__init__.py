"""
Módulo de extensiones para KMC Parser.

Este módulo proporciona la infraestructura para extender la funcionalidad
del parser KMC a través de plugins y otros mecanismos de extensión.
"""

from .plugin_base import KMCPlugin
from .auto_discovery import ExtensionDiscovery

# Crear un gestor de plugins accesible globalmente
from .plugin_manager import PluginManager, plugin_manager

__all__ = [
    "KMCPlugin",
    "ExtensionDiscovery",
    "PluginManager", 
    "plugin_manager"
]