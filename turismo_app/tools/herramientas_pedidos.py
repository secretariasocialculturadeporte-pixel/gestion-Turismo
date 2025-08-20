from langchain_core.tools import tool
from typing import Any, Dict, List
from turismo_app.database import db_manager

class PedidosSoldiers:
    """
    Herramientas para gestionar los pedidos de un restaurante.
    """
    def __init__(self, api_client: Any):
        self.user_id = api_client.get("user_id")

    @tool
    def crear_pedido_completo(self, datos_pedido: Dict, items_pedido: List[Dict]) -> Dict:
        """
        Crea un pedido completo, incluyendo los datos del pedido (tipo, cliente, etc.)
        y la lista de productos (items) que lo componen.
        """
        print(f"--- 💥 SOLDADO (Pedidos): ¡ACCIÓN! Creando un nuevo pedido completo. ---")

        # El user_id ya está en el contexto, pero lo pasamos explícitamente a la función de DB
        pedido_id = db_manager.crear_pedido_completo(
            datos_pedido=datos_pedido,
            items_pedido=items_pedido,
            audit_user_id=self.user_id
        )

        if pedido_id:
            return {"status": "success", "pedido_id": pedido_id}
        else:
            return {"status": "error", "message": "No se pudo crear el pedido."}

    def get_all_soldiers(self):
        return [self.crear_pedido_completo]
