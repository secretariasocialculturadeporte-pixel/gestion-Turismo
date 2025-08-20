from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from turismo_app.tools.herramientas_deportes import DeportesSoldiers

def get_deportes_sargento_graph():
    """
    Construye y devuelve el agente Sargento de Deportes.
    """
    def build_sargento_agent(state: SargentoBaseState):
        api_client = state.get("app_context")
        squad = DeportesSoldiers(api_client).get_all_soldiers()
        builder = SargentoGraphBuilder(squad, squad_name="Deportes")
        return builder.build_graph()

    print("✅ Doctrina DEAA-V2.1 aplicada: Sargento de Deportes listo para el despliegue.")
    return build_sargento_agent
