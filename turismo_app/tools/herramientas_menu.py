from langchain_core.tools import tool
from typing import Any, Dict
from ..database import db_manager

class MenuSoldiers:
    """
    Herramientas para gestionar el menú de un restaurante.
    """
    def __init__(self, api_client: Any):
        # El api_client podría ser un objeto que contiene el id_empresa
        self.empresa_id = api_client.get("empresa_id")
        self.user_id = api_client.get("user_id")

    @tool
    def crear_producto_menu(self, nombre: str, descripcion: str, precio: float, id_categoria: int) -> Dict:
        """Crea un nuevo producto en el menú."""
        print(f"--- 💥 SOLDADO (Menu): ¡ACCIÓN! Creando producto '{nombre}'. ---")
        datos = {
            "id_empresa": self.empresa_id,
            "nombre_producto": nombre,
            "descripcion": descripcion,
            "precio": precio,
            "id_categoria": id_categoria,
            "disponible": True,
            "audit_user_id": self.user_id
        }
        producto_id = db_manager.crear_o_actualizar_producto_menu(datos)
        if producto_id:
            return {"status": "success", "producto_id": producto_id}
        else:
            return {"status": "error", "message": "No se pudo crear el producto."}

    @tool
    def actualizar_producto_menu(self, id_producto: int, datos_actualizar: Dict) -> Dict:
        """Actualiza un producto existente en el menú."""
        print(f"--- 💥 SOLDADO (Menu): ¡ACCIÓN! Actualizando producto {id_producto}. ---")
        datos_actualizar["audit_user_id"] = self.user_id
        producto_id = db_manager.crear_o_actualizar_producto_menu(datos_actualizar, id_producto)
        if producto_id:
            return {"status": "success", "producto_id": producto_id}
        else:
            return {"status": "error", "message": "No se pudo actualizar el producto."}

    def get_all_soldiers(self):
        return [self.crear_producto_menu, self.actualizar_producto_menu]
