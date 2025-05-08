"""
Core components for KMC Parser.

This module contains the core components and utilities for the KMC (Kimfe Markdown Convention) parser.
"""
from .registry import registry, HandlerRegistry

__all__ = ["registry", "HandlerRegistry"]