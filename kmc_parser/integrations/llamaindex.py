"""
Integración de KMC Parser con LlamaIndex
"""
from typing import Dict, Any, Callable, Optional, List, Tuple, Union
from llama_index.core import VectorStoreIndex


class LlamaIndexHandler:
    """
    Handler para generar contenido usando LlamaIndex.
    
    Este handler permite usar las capacidades de búsqueda semántica y 
    generación de respuestas de LlamaIndex dentro de documentos KMC.
    """
    
    def __init__(
        self, 
        index: Optional[VectorStoreIndex] = None,
        query_engine: Optional[Any] = None,
        synthesizer: Optional[Any] = None,
        context_vars: Dict[str, Any] = None
    ):
        """
        Inicializa el handler de LlamaIndex.
        
        Args:
            index: Índice vectorial de LlamaIndex (opcional)
            query_engine: Motor de consultas personalizado (opcional)
            synthesizer: Sintetizador de respuestas personalizado (opcional)
            context_vars: Variables de contexto para usar en todas las consultas
        """
        self.index = index
        self.query_engine = query_engine
        self.synthesizer = synthesizer
        self.context_vars = context_vars or {}
        
        # Si se proporciona índice pero no query_engine, crear uno predeterminado
        if self.index is not None and self.query_engine is None:
            self.query_engine = self.index.as_query_engine()
    
    def __call__(self, var):
        """
        Genera contenido usando LlamaIndex basándose en el prompt.
        
        Esta implementación es compatible con la nueva API de KMC que pasa
        un objeto GenerativeVariable completo en lugar de parámetros separados.
        
        Args:
            var: Variable generativa (GenerativeVariable) o nombre de la variable (str)
            
        Returns:
            Contenido generado
        """
        # Compatibilidad con la API anterior
        if isinstance(var, str):
            var_name = var
            prompt = ""
            format_type = None
        else:
            # Nueva API: recibe un objeto GenerativeVariable completo
            var_name = var.name
            prompt = var.prompt
            format_type = var.parameters.get("format") if var.parameters else None
            
        if not prompt:
            prompt = f"Genera contenido relevante para {var_name}"
            
        if self.query_engine is None:
            raise ValueError("No se ha configurado un motor de consultas o índice en LlamaIndexHandler")
            
        # Reemplazar variables de contexto en el prompt si están presentes
        for key, value in self.context_vars.items():
            prompt = prompt.replace(f"{{{key}}}", str(value))
        
        # Realizar la consulta
        response = self.query_engine.query(prompt)
        
        # Retornar el texto de la respuesta
        return str(response)


class LlamaIndexQAHandler(LlamaIndexHandler):
    """
    Versión especializada para preguntas y respuestas.
    Optimizada para respuestas concisas y factuales.
    """
    
    def __init__(
        self,
        index: Optional[VectorStoreIndex] = None,
        **kwargs
    ):
        # Configurar un motor de consultas optimizado para QA
        if index is not None and "query_engine" not in kwargs:
            kwargs["query_engine"] = index.as_query_engine(
                response_mode="compact",
                similarity_top_k=3
            )
        super().__init__(index=index, **kwargs)


class LlamaIndexSummaryHandler(LlamaIndexHandler):
    """
    Versión especializada para generación de resúmenes.
    Optimizada para sintetizar información de múltiples fuentes.
    """
    
    def __init__(
        self,
        index: Optional[VectorStoreIndex] = None,
        **kwargs
    ):
        # Configurar un motor de consultas optimizado para resúmenes
        if index is not None and "query_engine" not in kwargs:
            kwargs["query_engine"] = index.as_query_engine(
                response_mode="tree_summarize",
                similarity_top_k=5
            )
        super().__init__(index=index, **kwargs)