from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from turismo_app.tools.herramientas_seguridad import SeguridadSoldiers

def get_seguridad_sargento_graph():
    """
    Construye y devuelve el agente Sargento de Seguridad y Auditoría.
    """
    def build_sargento_agent(state: SargentoBaseState):
        api_client = state.get("app_context")
        squad = SeguridadSoldiers(api_client).get_all_soldiers()
        builder = SargentoGraphBuilder(squad, squad_name="Seguridad y Auditoría")
        return builder.build_graph()

    print("✅ Doctrina DEAA-V2.1 aplicada: Sargento de Seguridad listo para el despliegue.")
    return build_sargento_agent
