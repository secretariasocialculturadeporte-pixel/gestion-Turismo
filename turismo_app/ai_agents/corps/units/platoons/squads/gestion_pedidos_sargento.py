from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from turismo_app.tools.herramientas_pedidos import PedidosSoldiers

def get_gestion_pedidos_sargento_graph():
    """
    Construye y devuelve el agente Sargento de Gestión de Pedidos.
    """
    def build_sargento_agent(state: SargentoBaseState):
        api_client = state.get("app_context")
        squad = PedidosSoldiers(api_client).get_all_soldiers()
        builder = SargentoGraphBuilder(squad, squad_name="Gestión de Pedidos")
        return builder.build_graph()

    print("✅ Doctrina DEAA-V2.1 aplicada: Sargento de Gestión de Pedidos listo para el despliegue.")
    return build_sargento_agent
