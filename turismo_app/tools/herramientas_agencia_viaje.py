from langchain_core.tools import tool
from typing import Any, List, Dict
from turismo_app.database import db_manager

class AgenciaViajeSoldiers:
    """
    Herramientas para gestionar las operaciones de una agencia de viajes.
    """
    def __init__(self, api_client: Any):
        self.empresa_id = api_client.get("empresa_id")
        self.user_id = api_client.get("user_id")

    @tool
    def crear_paquete_turistico(self, nombre_paquete: str, descripcion: str, precio_total: float, duracion_dias: int) -> Dict:
        """Crea un nuevo paquete turístico."""
        print(f"--- 💥 SOLDADO (Agencia): ¡ACCIÓN! Creando paquete '{nombre_paquete}'. ---")
        datos = {
            "id_empresa": self.empresa_id,
            "nombre_paquete": nombre_paquete,
            "descripcion": descripcion,
            "precio_total": precio_total,
            "duracion_dias": duracion_dias,
            "activo": True,
            "audit_user_id": self.user_id
        }
        paquete_id = db_manager.crear_o_actualizar_paquete(datos)
        if paquete_id:
            return {"status": "success", "id_paquete": paquete_id}
        else:
            return {"status": "error", "message": "No se pudo crear el paquete."}

    @tool
    def agregar_servicio_a_paquete(self, id_paquete: int, tipo_servicio: str, id_servicio_especifico: int, descripcion_servicio: str) -> Dict:
        """Agrega un servicio (hotel, tour, etc.) a un paquete turístico existente."""
        print(f"--- 💥 SOLDADO (Agencia): ¡ACCIÓN! Agregando servicio al paquete {id_paquete}. ---")
        datos = {
            "id_paquete": id_paquete,
            "tipo_servicio": tipo_servicio,
            "id_servicio_especifico": id_servicio_especifico,
            "descripcion_servicio": descripcion_servicio
        }
        servicio_id = db_manager.agregar_servicio_a_paquete(datos, self.user_id)
        if servicio_id:
            return {"status": "success", "id_paquete_servicio": servicio_id}
        else:
            return {"status": "error", "message": "No se pudo agregar el servicio al paquete."}

    @tool
    def crear_reserva_paquete(self, id_paquete: int, id_cliente: int, fecha_inicio: str, numero_personas: int) -> Dict:
        """Crea una reserva para un paquete turístico."""
        print(f"--- 💥 SOLDADO (Agencia): ¡ACCIÓN! Creando reserva para el paquete {id_paquete}. ---")
        datos = {
            "id_paquete": id_paquete,
            "id_cliente": id_cliente,
            "fecha_inicio": fecha_inicio,
            "numero_personas": numero_personas,
            "estado": "Confirmada",
            "audit_user_id": self.user_id
        }
        reserva_id = db_manager.crear_o_actualizar_reserva_paquete(datos)
        if reserva_id:
            return {"status": "success", "id_reserva_paquete": reserva_id}
        else:
            return {"status": "error", "message": "No se pudo crear la reserva del paquete."}

    def get_all_soldiers(self) -> List:
        return [
            self.crear_paquete_turistico,
            self.agregar_servicio_a_paquete,
            self.crear_reserva_paquete
        ]
