from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from turismo_app.tools.herramientas_comunicaciones import ComunicacionesSoldiers

def get_comunicaciones_sargento_graph():
    """
    Construye y devuelve el agente Sargento de Comunicaciones.
    """
    def build_sargento_agent(state: SargentoBaseState):
        api_client = state.get("app_context")
        squad = ComunicacionesSoldiers(api_client).get_all_soldiers()
        builder = SargentoGraphBuilder(squad, squad_name="Comunicación y Notificaciones")
        return builder.build_graph()

    print("✅ Doctrina DEAA-V2.1 aplicada: Sargento de Comunicaciones listo para el despliegue.")
    return build_sargento_agent
