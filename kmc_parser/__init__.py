"""
KMC Parser - Core parser para Kimfe Markdown Convention
"""

from .parser import KMCParser
from .models import (
    ContextualVariable, 
    MetadataVariable, 
    GenerativeVariable, 
    KMCDocument,
    KMCVariableDefinition
)

# Exponer componentes de la arquitectura expandible
from .core import registry
from .handlers import (
    BaseHandler,
    ContextHandler,
    MetadataHandler,
    GenerativeHandler,
    context_handler,
    metadata_handler,
    generative_handler
)
from .extensions import KMCPlugin, plugin_manager

__version__ = "0.3.0"

__all__ = [
    "KMCParser",
    "ContextualVariable",
    "MetadataVariable",
    "GenerativeVariable",
    "KMCDocument",
    "KMCVariableDefinition",
    # Componentes de la arquitectura expandible
    "registry",
    "BaseHandler",
    "ContextHandler",
    "MetadataHandler",
    "GenerativeHandler",
    "context_handler",
    "metadata_handler",
    "generative_handler",
    "KMCPlugin",
    "plugin_manager"
]