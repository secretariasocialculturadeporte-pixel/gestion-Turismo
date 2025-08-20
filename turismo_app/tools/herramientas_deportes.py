from langchain_core.tools import tool
from typing import Any, List, Dict
from turismo_app.database import db_manager

class DeportesSoldiers:
    """
    El arsenal de herramientas de ejecución para las operaciones deportivas.
    """
    def __init__(self, api_client: Any):
        self.empresa_id = api_client.get("empresa_id")
        self.user_id = api_client.get("user_id")

    @tool
    def crear_torneo(self, nombre_torneo: str, deporte: str, fecha_inicio: str) -> Dict:
        """(SOLDADO TORNEOS) Ejecuta la creación de un nuevo torneo o competición."""
        print(f"--- 💥 SOLDADO (Deportes): ¡ACCIÓN! Creando torneo '{nombre_torneo}' de {deporte}. ---")
        datos = {
            "id_empresa": self.empresa_id,
            "nombre": nombre_torneo,
            "descripcion": f"Torneo de {deporte}",
            "tipo_oferta": "Torneo",
            "fecha_inicio": fecha_inicio,
            "audit_user_id": self.user_id
        }
        torneo_id = db_manager.crear_clase_evento(datos)
        if torneo_id:
            return {"status": "success", "torneo_id": torneo_id}
        else:
            return {"status": "error", "message": "No se pudo crear el torneo."}

    @tool
    def inscribir_equipo_a_torneo(self, torneo_id: int, id_participantes: List[int]) -> Dict:
        """(SOLDADO INSCRIPCIONES) Inscribe un equipo con sus participantes a un torneo existente."""
        print(f"--- 💥 SOLDADO (Deportes): ¡ACCIÓN! Inscribiendo equipo al torneo {torneo_id}. ---")
        success = db_manager.inscribir_equipo_a_evento(torneo_id, id_participantes, self.user_id)
        if success:
            return {"status": "success", "message": f"Equipo inscrito al torneo {torneo_id}."}
        else:
            return {"status": "error", "message": "No se pudo inscribir al equipo."}

    @tool
    def registrar_resultado_partido(self, torneo_id: int, partido_id: str, marcador: str) -> Dict:
        """(SIMULADO) Registra el marcador final de un partido o encuentro."""
        print(f"--- 💥 SOLDADO (Deportes): ¡ACCIÓN SIMULADA! Registrando resultado del partido {partido_id}: {marcador}. ---")
        return {"status": "success", "partido_id": partido_id}

    @tool
    def reservar_instalacion_deportiva(self, instalacion_id: int, fecha: str, hora_inicio: str, hora_fin: str) -> Dict:
        """(SIMULADO) Reserva una instalación deportiva (cancha, piscina, etc.)."""
        print(f"--- 💥 SOLDADO (Deportes): ¡ACCIÓN SIMULADA! Reservando instalación {instalacion_id} para el {fecha}. ---")
        return {"status": "success", "reserva_id": f"reserva_inst_{instalacion_id}_{fecha}"}

    def get_all_soldiers(self) -> List:
        """Recluta y devuelve la Escuadra de Deportes."""
        return [
            self.crear_torneo,
            self.inscribir_equipo_a_torneo,
            self.registrar_resultado_partido,
            self.reservar_instalacion_deportiva,
        ]
