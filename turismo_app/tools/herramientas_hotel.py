from langchain_core.tools import tool
from typing import Any, List, Dict
from turismo_app.database import db_manager

class HotelSoldiers:
    """
    Herramientas para gestionar las operaciones de un hotel.
    """
    def __init__(self, api_client: Any):
        self.empresa_id = api_client.get("empresa_id")
        self.user_id = api_client.get("user_id")

    @tool
    def crear_tipo_habitacion(self, nombre_tipo: str, capacidad: int, precio_base: float, descripcion: str = "") -> Dict:
        """Crea un nuevo tipo de habitación (como un recurso reservable)."""
        print(f"--- 💥 SOLDADO (Hotel): ¡ACCIÓN! Creando tipo de habitación '{nombre_tipo}'. ---")
        datos = {
            "id_empresa": self.empresa_id,
            "nombre_recurso": nombre_tipo,
            "tipo_recurso": "Habitacion",
            "capacidad": capacidad,
            "precio_base": precio_base,
            "descripcion": descripcion,
            "audit_user_id": self.user_id
        }
        recurso_id = db_manager.crear_o_actualizar_recurso(datos)
        if recurso_id:
            return {"status": "success", "id_tipo_habitacion": recurso_id}
        else:
            return {"status": "error", "message": "No se pudo crear el tipo de habitación."}

    @tool
    def buscar_habitaciones_disponibles(self, fecha_inicio: str, fecha_fin: str, capacidad: int = 1) -> List[Dict]:
        """Busca habitaciones disponibles para un rango de fechas y capacidad de personas."""
        print(f"--- 💥 SOLDADO (Hotel): ¡ACCIÓN! Buscando habitaciones disponibles del {fecha_inicio} al {fecha_fin}. ---")
        habitaciones = db_manager.buscar_habitaciones_disponibles(self.empresa_id, fecha_inicio, fecha_fin, capacidad)
        return habitaciones

    @tool
    def crear_reserva_hotel(self, id_habitacion: int, id_cliente: int, fecha_inicio: str, fecha_fin: str) -> Dict:
        """Crea una reserva para una habitación específica."""
        print(f"--- 💥 SOLDADO (Hotel): ¡ACCIÓN! Creando reserva para habitación {id_habitacion}. ---")
        datos = {
            "id_recurso": id_habitacion,
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
            return {"status": "error", "message": "No se pudo crear la reserva."}

    def get_all_soldiers(self) -> List:
        return [
            self.crear_tipo_habitacion,
            self.buscar_habitaciones_disponibles,
            self.crear_reserva_hotel
        ]
