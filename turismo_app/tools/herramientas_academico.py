from langchain_core.tools import tool
from typing import Any, List, Dict
from turismo_app.database import db_manager

class AcademicoSoldiers:
    """
    Herramientas para operaciones académicas y deportivas.
    """
    def __init__(self, api_client: Any):
        self.empresa_id = api_client.get("empresa_id")
        self.user_id = api_client.get("user_id")

    @tool
    def crear_clase(self, nombre_clase: str, descripcion: str) -> Dict:
        """Crea una nueva clase, taller o curso."""
        print(f"--- 💥 SOLDADO (Clases): ¡ACCIÓN! Creando la clase '{nombre_clase}'. ---")
        datos = {
            "id_empresa": self.empresa_id,
            "nombre": nombre_clase,
            "descripcion": descripcion,
            "tipo_oferta": "Clase",
            "audit_user_id": self.user_id
        }
        clase_id = db_manager.crear_clase_evento(datos)
        if clase_id:
            return {"status": "success", "clase_id": clase_id}
        else:
            return {"status": "error", "message": "No se pudo crear la clase."}

    @tool
    def abrir_inscripciones_clase(self, clase_id: int, cupos_disponibles: int) -> Dict:
        """Abre el proceso de inscripción para una clase, definiendo los cupos."""
        print(f"--- 💥 SOLDADO (Inscripciones): ¡ACCIÓN! Abriendo {cupos_disponibles} cupos para la clase {clase_id}. ---")
        datos = {"cupos_disponibles": cupos_disponibles}
        result_id = db_manager.crear_o_actualizar_producto_evento(datos, clase_id)
        if result_id:
            return {"status": "success", "message": f"{cupos_disponibles} cupos abiertos para la clase {clase_id}."}
        else:
            return {"status": "error", "message": "No se pudo abrir las inscripciones."}

    @tool
    def inscribir_estudiante_en_clase(self, clase_id: int, estudiante_id: int) -> Dict:
        """Inscribe a un estudiante en una clase específica."""
        print(f"--- 💥 SOLDADO (Inscripciones): ¡ACCIÓN! Inscribiendo estudiante {estudiante_id} a la clase {clase_id}. ---")
        inscripcion_id = db_manager.inscribir_usuario_a_evento(clase_id, estudiante_id, self.user_id)
        if inscripcion_id:
            return {"status": "success", "inscripcion_id": inscripcion_id}
        else:
            return {"status": "error", "message": "No se pudo inscribir al estudiante."}

    @tool
    def asignar_instructor_a_clase(self, clase_id: int, instructor_id: int) -> Dict:
        """(SIMULADO) Asigna un instructor a una clase."""
        print(f"--- 💥 SOLDADO (Instructores): ¡ACCIÓN SIMULADA! Asignando instructor {instructor_id} a clase {clase_id}. ---")
        return {"status": "success", "message": "Instructor asignado (simulado)."}

    @tool
    def registrar_asistencia_clase(self, clase_id: int, id_estudiantes_presentes: List[int]) -> Dict:
        """(SIMULADO) Registra la asistencia a una clase."""
        print(f"--- 💥 SOLDADO (Asistencia): ¡ACCIÓN SIMULADA! Registrando asistencia para clase {clase_id}. ---")
        return {"status": "success", "asistencia_registrada": len(id_estudiantes_presentes)}

    def get_all_soldiers(self) -> List:
        return [
            self.crear_clase,
            self.abrir_inscripciones_clase,
            self.inscribir_estudiante_en_clase,
            self.asignar_instructor_a_clase,
            self.registrar_asistencia_clase
        ]
