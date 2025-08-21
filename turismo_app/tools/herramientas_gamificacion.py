from langchain_core.tools import tool
from typing import Any, List, Dict
from turismo_app.database import db_manager

class GamificacionSoldiers:
    """
    El arsenal de herramientas de ejecución para la escuadra de Gamificación (SIGA).
    """
    def __init__(self, api_client: Any):
        self.user_id = api_client.get("user_id")

    @tool
    def conceder_puntos_a_estudiante(self, estudiante_id: int, cantidad_puntos: int, motivo: str) -> Dict:
        """(SOLDADO PUNTOS) Concede una cantidad específica de puntos a un estudiante por un motivo."""
        print(f"--- 💥 SOLDADO (Puntos): ¡ACCIÓN! Concediendo {cantidad_puntos} puntos a estudiante {estudiante_id}. ---")
        success = db_manager.conceder_puntos(estudiante_id, cantidad_puntos, motivo, self.user_id)
        if success:
            return {"status": "success", "message": f"{cantidad_puntos} puntos concedidos."}
        else:
            return {"status": "error", "message": "No se pudieron conceder los puntos."}

    @tool
    def crear_medalla(self, nombre: str, descripcion: str, icono: str = "emoji_events") -> Dict:
        """Crea un nuevo tipo de medalla o logro que puede ser otorgado."""
        print(f"--- 💥 SOLDADO (Medallas): ¡ACCIÓN! Creando medalla '{nombre}'. ---")
        medalla_id = db_manager.crear_medalla(nombre, descripcion, icono, self.user_id)
        if medalla_id:
            return {"status": "success", "id_medalla": medalla_id}
        else:
            return {"status": "error", "message": "No se pudo crear la medalla."}

    @tool
    def buscar_medalla_por_nombre(self, nombre_medalla: str) -> Dict:
        """Busca una medalla por su nombre para obtener su ID."""
        print(f"--- 💥 SOLDADO (Medallas): ¡ACCIÓN! Buscando medalla '{nombre_medalla}'. ---")
        medalla = db_manager.get_medalla_por_nombre(nombre_medalla)
        if medalla:
            return {"status": "success", "id_medalla": medalla["id_medalla"]}
        else:
            return {"status": "not_found", "message": f"No se encontró la medalla '{nombre_medalla}'."}

    @tool
    def otorgar_medalla_a_usuario(self, id_usuario: int, id_medalla: int) -> Dict:
        """Otorga una medalla específica (por ID) a un usuario específico (por ID)."""
        print(f"--- 💥 SOLDADO (Medallas): ¡ACCIÓN! Otorgando medalla {id_medalla} a usuario {id_usuario}. ---")
        success = db_manager.otorgar_medalla(id_usuario, id_medalla, self.user_id)
        if success:
            return {"status": "success", "message": "Medalla otorgada con éxito."}
        else:
            return {"status": "error", "message": "No se pudo otorgar la medalla."}

    @tool
    def actualizar_nivel_por_puntos(self, estudiante_id: int) -> Dict:
        """(SIMULADO) Comprueba el total de puntos de un estudiante y actualiza su nivel."""
        print(f"--- 💥 SOLDADO (Niveles): ¡ACCIÓN SIMULADA! Verificando nivel para estudiante {estudiante_id}. ---")
        return {"status": "success", "new_level": 5, "message": "Nivel actualizado (simulado)."}

    @tool
    def generar_tabla_de_clasificacion(self, tipo_ranking: str) -> List[Dict]:
        """(SIMULADO) Genera una tabla de clasificación (ranking)."""
        print(f"--- 💥 SOLDADO (Rankings): ¡ACCIÓN SIMULADA! Generando ranking '{tipo_ranking}'. ---")
        return [{"rank": 1, "name": "Usuario_A", "points": 150}, {"rank": 2, "name": "Usuario_B", "points": 145}]

    def get_all_soldiers(self) -> List:
        return [
            self.conceder_puntos_a_estudiante,
            self.crear_medalla,
            self.buscar_medalla_por_nombre,
            self.otorgar_medalla_a_usuario,
            self.actualizar_nivel_por_puntos,
            self.generar_tabla_de_clasificacion
        ]
