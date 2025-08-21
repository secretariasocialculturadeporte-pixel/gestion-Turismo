from langchain_core.tools import tool
from typing import Any, List, Dict
from turismo_app.database import db_manager

class TransporteSoldiers:
    """
    Herramientas para gestionar las operaciones de transporte turístico.
    """
    def __init__(self, api_client: Any):
        self.empresa_id = api_client.get("empresa_id")
        self.user_id = api_client.get("user_id")

    @tool
    def crear_vehiculo(self, nombre_vehiculo: str, capacidad: int, precio_base: float, descripcion: str = "") -> Dict:
        """Crea un nuevo vehículo (como un recurso reservable)."""
        print(f"--- 💥 SOLDADO (Transporte): ¡ACCIÓN! Creando vehículo '{nombre_vehiculo}'. ---")
        datos = {
            "id_empresa": self.empresa_id,
            "nombre_recurso": nombre_vehiculo,
            "tipo_recurso": "Transporte",
            "capacidad": capacidad,
            "precio_base": precio_base,
            "descripcion": descripcion,
            "audit_user_id": self.user_id
        }
        recurso_id = db_manager.crear_o_actualizar_recurso(datos)
        if recurso_id:
            return {"status": "success", "id_vehiculo": recurso_id}
        else:
            return {"status": "error", "message": "No se pudo crear el vehículo."}

    @tool
    def buscar_vehiculos_disponibles(self, fecha_inicio: str, fecha_fin: str, capacidad: int = 1) -> List[Dict]:
        """Busca vehículos disponibles para un rango de fechas y capacidad de pasajeros."""
        print(f"--- 💥 SOLDADO (Transporte): ¡ACCIÓN! Buscando vehículos disponibles del {fecha_inicio} al {fecha_fin}. ---")
        vehiculos = db_manager.buscar_recursos_disponibles(self.empresa_id, "Transporte", fecha_inicio, fecha_fin, capacidad)
        return vehiculos

    @tool
    def reservar_vehiculo(self, id_vehiculo: int, id_cliente: int, fecha_inicio: str, fecha_fin: str) -> Dict:
        """Crea una reserva para un vehículo específico."""
        print(f"--- 💥 SOLDADO (Transporte): ¡ACCIÓN! Creando reserva para vehículo {id_vehiculo}. ---")
        datos = {
            "id_recurso": id_vehiculo,
            "id_cliente": id_cliente,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "estado": "Confirmada",
            "audit_user_id": self.user_id
        }
        reserva_id = db_manager.crear_o_actualizar_reserva(datos)
        if reserva_id:
            return {"status": "success", "id_reserva": reserva_id}
        else:
            return {"status": "error", "message": "No se pudo crear la reserva del vehículo."}

    def get_all_soldiers(self) -> List:
        return [
            self.crear_vehiculo,
            self.buscar_vehiculos_disponibles,
            self.reservar_vehiculo
        ]
