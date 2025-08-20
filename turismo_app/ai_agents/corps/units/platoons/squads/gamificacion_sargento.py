from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from turismo_app.tools.herramientas_gamificacion import GamificacionSoldiers

def get_gamificacion_sargento_graph():
    """
    Construye y devuelve el agente Sargento de Gamificación (SIGA).
    """
    def build_sargento_agent(state: SargentoBaseState):
        api_client = state.get("app_context")
        squad = GamificacionSoldiers(api_client).get_all_soldiers()
        builder = SargentoGraphBuilder(squad, squad_name="Gamificación (SIGA)")
        return builder.build_graph()

    print("✅ Doctrina DEAA-V2.1 aplicada: Sargento de Gamificación listo para el despliegue.")
    return build_sargento_agent
