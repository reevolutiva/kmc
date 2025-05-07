"""
Document Metadata Handler - Handler para variables de metadata de documento [{doc:nombre}]
"""
from typing import Dict, Any, Optional
import os
import json

from ...handlers.base import MetadataHandler, metadata_handler


@metadata_handler("doc")
class DocumentMetadataHandler(MetadataHandler):
    """
    Handler para variables de metadata de documento.
    
    Este handler gestiona variables como [{doc:version}], [{doc:titulo}], etc.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Inicializa el handler de metadata de documento.
        
        Args:
            config: Configuración del handler, puede incluir:
                - doc_id: ID del documento
                - metadata: Datos de metadata directamente (dict)
                - metadata_path: Ruta al archivo JSON con metadata
        """
        super().__init__(config)
        self.metadata = {}
        self._load_metadata()
    
    def _load_metadata(self):
        """Carga metadata del documento desde la configuración o archivo"""
        # Prioridad 1: Datos directos en configuración
        if "metadata" in self.config:
            self.metadata = self.config["metadata"]
            return
        
        # Prioridad 2: Cargar desde archivo JSON si se proporciona una ruta
        if "metadata_path" in self.config:
            path = self.config["metadata_path"]
            if os.path.exists(path):
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        self.metadata = json.load(f)
                    return
                except Exception as e:
                    self.logger.error(f"Error al cargar metadata desde {path}: {str(e)}")
        
        # Prioridad 3: Cargar datos por defecto
        doc_id = self.config.get("doc_id", "default")
        self.metadata = self._get_default_metadata(doc_id)
    
    def _get_default_metadata(self, doc_id: str) -> Dict[str, Any]:
        """
        Genera metadata por defecto para un documento.
        
        Args:
            doc_id: ID del documento
            
        Returns:
            Metadata por defecto
        """
        return {
            "titulo": f"Documento {doc_id}",
            "version": "1.0",
            "autor": "Sistema KMC",
            "fecha": "2025-05-07",
            "estado": "Borrador",
            "tipo_documento": "Informe",
            "categoría": "General"
        }
    
    def _get_metadata_value(self, var_name: str) -> Any:
        """
        Obtiene el valor de una variable de metadata.
        
        Args:
            var_name: Nombre de la variable de metadata
            
        Returns:
            Valor de la metadata o placeholder si no existe
        """
        return self.metadata.get(var_name, f"<doc:{var_name}>")