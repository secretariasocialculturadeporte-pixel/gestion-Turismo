from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from turismo_app.tools.herramientas_menu import MenuSoldiers

def get_gestion_menu_sargento_graph():
    """
    Construye y devuelve el agente Sargento de Gestión de Menú.
    """
    def build_sargento_agent(state: SargentoBaseState):
        api_client = state.get("app_context")
        squad = MenuSoldiers(api_client).get_all_soldiers()
        builder = SargentoGraphBuilder(squad, squad_name="Gestión de Menú")
        return builder.build_graph()

    print("✅ Doctrina DEAA-V2.1 aplicada: Sargento de Gestión de Menú listo para el despliegue.")
    return build_sargento_agent
