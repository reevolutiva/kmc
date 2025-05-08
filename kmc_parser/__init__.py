"""
KMC Parser - Implementation of the Kimfe Markdown Convention.

This package provides tools for processing Markdown files with enhanced variable support
according to the Kimfe Markdown Convention (KMC).
"""

__version__ = "1.0.0"

# Import main classes for easier access
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