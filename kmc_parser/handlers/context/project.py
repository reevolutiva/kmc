"""
Project Handler - Handler para variables contextuales de proyecto [[project:nombre]]
"""
from typing import Dict, Any, Optional
import os
import json

from ...handlers.base import ContextHandler, context_handler


@context_handler("project")
class ProjectHandler(ContextHandler):
    """
    Handler para variables contextuales de tipo proyecto.
    
    Este handler gestiona variables como [[project:nombre]], [[project:descripcion]], etc.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Inicializa el handler de proyecto.
        
        Args:
            config: Configuración del handler, puede incluir:
                - project_id: ID del proyecto
                - project_data: Datos del proyecto (dict)
                - project_path: Ruta al archivo JSON con datos del proyecto
        """
        super().__init__(config)
        self.project_data = {}
        self._load_project_data()
    
    def _load_project_data(self):
        """Carga datos del proyecto desde la configuración o archivo"""
        # Prioridad 1: Datos directos en configuración
        if "project_data" in self.config:
            self.project_data = self.config["project_data"]
            return
        
        # Prioridad 2: Cargar desde archivo JSON si se proporciona una ruta
        if "project_path" in self.config:
            path = self.config["project_path"]
            if os.path.exists(path):
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        self.project_data = json.load(f)
                    return
                except Exception as e:
                    self.logger.error(f"Error al cargar datos de proyecto desde {path}: {str(e)}")
        
        # Prioridad 3: Cargar datos simulados si hay un project_id o usar valores por defecto
        project_id = self.config.get("project_id", "default")
        self.project_data = self._get_mock_data(project_id)
    
    def _get_mock_data(self, project_id: str) -> Dict[str, Any]:
        """
        Genera datos de ejemplo para un proyecto.
        
        Args:
            project_id: ID del proyecto
            
        Returns:
            Datos simulados del proyecto
        """
        return {
            "nombre": f"Proyecto {project_id.title()}",
            "descripcion": f"Descripción del proyecto {project_id}",
            "fecha_inicio": "2025-05-07",
            "estado": "Activo",
            "cliente": "Cliente Demo",
            "responsable": "Giorgio La Pietra",
            "presupuesto": "50000",
            "tipo": "Desarrollo de Software"
        }
    
    def _get_context_value(self, var_name: str) -> Any:
        """
        Obtiene el valor de una variable contextual de proyecto.
        
        Args:
            var_name: Nombre de la variable de proyecto
            
        Returns:
            Valor de la variable o placeholder si no existe
        """
        return self.project_data.get(var_name, f"<project:{var_name}>")