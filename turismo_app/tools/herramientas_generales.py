from langchain_core.tools import tool
from typing import Any, Dict
from turismo_app.database import db_manager

class GeneralesSoldiers:
    """
    Herramientas generales que pueden ser útiles para múltiples agentes.
    """
    def __init__(self, api_client: Any = None):
        pass

    @tool
    def buscar_empresa_por_nombre(self, nombre_empresa: str) -> Dict:
        """Busca una empresa por su nombre y devuelve su ID."""
        print(f"--- 💥 SOLDADO (General): ¡ACCIÓN! Buscando empresa '{nombre_empresa}'. ---")
        empresa = db_manager.obtener_empresa_por_nombre(nombre_empresa)
        if empresa:
            return {"status": "success", "id_empresa": empresa["id_empresa"]}
        else:
            return {"status": "error", "message": f"No se encontró la empresa '{nombre_empresa}'."}

    @tool
    def buscar_servicio_por_nombre(self, nombre_servicio: str) -> Dict:
        """Busca un servicio (como un tour, un hotel, etc.) por su nombre y devuelve su ID y tipo."""
        print(f"--- 💥 SOLDADO (General): ¡ACCIÓN! Buscando servicio '{nombre_servicio}'. ---")
        servicio = db_manager.buscar_servicio_por_nombre(nombre_servicio)
        if servicio:
            return {"status": "success", "id_servicio": servicio["id"], "tipo_servicio": servicio["tipo"]}
        else:
            return {"status": "error", "message": f"No se encontró el servicio '{nombre_servicio}'."}

    def get_all_soldiers(self):
        return [self.buscar_empresa_por_nombre, self.buscar_servicio_por_nombre]
