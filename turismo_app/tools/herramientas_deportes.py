from langchain_core.tools import tool
from typing import Any, List, Dict

class DeportesSoldiers:
    """
    El arsenal de herramientas de ejecución para las operaciones deportivas.
    """
    def __init__(self, api_client: Any):
        self.api = api_client

    @tool
    def crear_torneo(self, nombre_torneo: str, deporte: str, fecha_inicio: str) -> Dict:
        """(SOLDADO TORNEOS) Ejecuta la creación de un nuevo torneo o competición."""
        print(f"--- 💥 SOLDADO (Deportes): ¡ACCIÓN! Creando torneo '{nombre_torneo}' de {deporte}. ---")
        return {"status": "success", "torneo_id": f"torneo_{nombre_torneo.lower().replace(' ', '_')}"}

    @tool
    def inscribir_equipo_a_torneo(self, torneo_id: str, nombre_equipo: str, id_participantes: List[int]) -> Dict:
        """(SOLDADO INSCRIPCIONES) Inscribe un equipo con sus participantes a un torneo existente."""
        print(f"--- 💥 SOLDADO (Deportes): ¡ACCIÓN! Inscribiendo equipo '{nombre_equipo}' al torneo {torneo_id}. ---")
        return {"status": "success", "inscripcion_id": f"insc_{nombre_equipo.lower()}"}

    @tool
    def registrar_resultado_partido(self, torneo_id: str, partido_id: str, marcador: str) -> Dict:
        """(SOLDADO RESULTADOS) Registra el marcador final de un partido o encuentro."""
        print(f"--- 💥 SOLDADO (Deportes): ¡ACCIÓN! Registrando resultado del partido {partido_id}: {marcador}. ---")
        return {"status": "success", "partido_id": partido_id}

    @tool
    def reservar_instalacion_deportiva(self, instalacion_id: int, fecha: str, hora_inicio: str, hora_fin: str) -> Dict:
        """(SOLDADO INSTALACIONES) Reserva una instalación deportiva (cancha, piscina, etc.) para un evento o partido."""
        print(f"--- 💥 SOLDADO (Deportes): ¡ACCIÓN! Reservando instalación {instalacion_id} para el {fecha}. ---")
        return {"status": "success", "reserva_id": f"reserva_inst_{instalacion_id}_{fecha}"}

    def get_all_soldiers(self) -> List:
        """Recluta y devuelve la Escuadra de Deportes."""
        return [
            self.crear_torneo,
            self.inscribir_equipo_a_torneo,
            self.registrar_resultado_partido,
            self.reservar_instalacion_deportiva,
        ]
