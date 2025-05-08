"""
Integración específica de KMC con la infraestructura de Kimfe/itscop
"""
import os
import sys
from typing import Dict, Any, Callable, Optional, List, Union

# Añadir directorio principal para importación de módulos itscop
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from src.utils.index import FAISSIndex
from src.utils.llamaindex import LlamaIndexMiddleware
from src.utils.documentBuilder import DocumentBuilder
from src.models.models import ChainFactory, ChainConfig

from ..parser import KMCParser


class ITSCOPIntegration:
    """
    Integración específica para el sistema Kimfe/itscop.
    
    Esta clase facilita la conexión entre el parser KMC y la infraestructura
    existente de Kimfe, incluyendo índices FAISS, middleware LlamaIndex,
    y herramientas de construcción de documentos.
    """
    
    def __init__(
        self,
        project_id: Optional[str] = None,
        user_id: Optional[str] = None,
        org_id: Optional[str] = None,
        kb_ids: Optional[List[str]] = None,
    ):
        """
        Inicializa la integración con itscop.
        
        Args:
            project_id: ID del proyecto (opcional)
            user_id: ID del usuario (opcional) 
            org_id: ID de la organización (opcional)
            kb_ids: Lista de IDs de bases de conocimiento para indexar (opcional)
        """
        self.project_id = project_id
        self.user_id = user_id
        self.org_id = org_id
        self.kb_ids = kb_ids or []
        
        # Inicializa componentes de itscop
        self.index = None
        self.middleware = None
        self.parser = KMCParser()
        self.doc_builder = DocumentBuilder()
        
        # Configura los componentes necesarios si se proporcionan IDs
        if self.project_id or self.kb_ids:
            self._setup_components()
    
    def _setup_components(self):
        """Configura los componentes necesarios para la integración"""
        # Inicializa el índice FAISS
        self.index = FAISSIndex()
        
        # Añade documentos de KB al índice
        for kb_id in self.kb_ids:
            try:
                self.index.add_document(kb_id)
            except Exception as e:
                print(f"Error al añadir documento KB {kb_id}: {str(e)}")
        
        # Inicializa middleware LlamaIndex
        if self.index.index:
            self.middleware = LlamaIndexMiddleware(index=self.index.index)
            
            # Registra handlers para diferentes tipos de variables generativas
            from .kmc_llamaindex_bridge import LlamaIndexHandler, LlamaIndexQAHandler, LlamaIndexSummaryHandler
            
            # Handlers para diferentes tipos de consulta
            qa_handler = LlamaIndexQAHandler(query_engine=self.middleware.create_query_engine())
            summary_handler = LlamaIndexSummaryHandler(query_engine=self.middleware.create_summary_engine())
            
            # Registra los handlers en el parser
            self.parser.register_generative_handler("ai:gpt4", qa_handler)
            self.parser.register_generative_handler("ai:summary", summary_handler)
            self.parser.register_generative_handler("ai:qa", qa_handler)
    
    def load_context_data(self):
        """
        Carga datos contextuales (proyecto, usuario, org) y configura los handlers correspondientes
        """
        # En una implementación real, esto cargaría datos de la base de datos
        if self.project_id:
            # Ejemplo: Carga datos del proyecto desde BD
            project_data = self._mock_project_data(self.project_id)
            
            def project_handler(var_name):
                return project_data.get(var_name, f"[[project:{var_name} - No encontrado]]")
            
            self.parser.register_context_handler("project", project_handler)
        
        if self.org_id:
            # Ejemplo: Carga datos de organización desde BD
            org_data = self._mock_org_data(self.org_id)
            
            def org_handler(var_name):
                return org_data.get(var_name, f"[[org:{var_name} - No encontrado]]")
            
            self.parser.register_context_handler("org", org_handler)
            
        if self.user_id:
            # Ejemplo: Carga datos de usuario desde BD
            user_data = self._mock_user_data(self.user_id)
            
            def user_handler(var_name):
                return user_data.get(var_name, f"[[user:{var_name} - No encontrado]]")
            
            self.parser.register_context_handler("user", user_handler)
    
    def register_document_metadata(self, metadata: Dict[str, Any]):
        """
        Registra metadata de documento para renderizado
        
        Args:
            metadata: Diccionario con metadata del documento
        """
        def doc_handler(var_name):
            return metadata.get(var_name, f"[{{doc:{var_name} - No encontrado}}]")
        
        self.parser.register_metadata_handler("doc", doc_handler)
    
    def render_document(self, content: str, document_id: Optional[str] = None) -> str:
        """
        Renderiza un documento KMC completo
        
        Args:
            content: Contenido KMC a renderizar
            document_id: ID del documento (opcional)
            
        Returns:
            Documento renderizado
        """
        # Renderiza el documento con KMC
        rendered_content = self.parser.render(content)
        
        # Si se proporciona ID de documento, construye el documento final
        if document_id:
            return self.doc_builder.build_from_markdown(rendered_content, document_id)
        
        return rendered_content
    
    def _mock_project_data(self, project_id: str) -> Dict[str, str]:
        """Mock de datos de proyecto para ejemplos"""
        return {
            "nombre": f"Proyecto {project_id}",
            "descripcion": "Este es un proyecto de demostración",
            "fecha_inicio": "2025-05-07",
            "industria": "Tecnología"
        }
    
    def _mock_org_data(self, org_id: str) -> Dict[str, str]:
        """Mock de datos de organización para ejemplos"""
        return {
            "nombre_empresa": "Kimfe",
            "dominio": "kimfe.com",
            "industria": "Tecnología",
            "pais": "Chile"
        }
    
    def _mock_user_data(self, user_id: str) -> Dict[str, str]:
        """Mock de datos de usuario para ejemplos"""
        return {
            "nombre_completo": "Usuario Demo",
            "email": "demo@kimfe.com",
            "rol": "Desarrollador"
        }