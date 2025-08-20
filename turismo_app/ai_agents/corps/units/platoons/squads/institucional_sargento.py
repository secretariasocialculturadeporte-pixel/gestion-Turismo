from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from turismo_app.tools.herramientas_institucional import InstitucionalSoldiers

def get_institucional_sargento_graph():
    """
    Construye y devuelve el agente Sargento de Gestión Institucional.
    """
    def build_sargento_agent(state: SargentoBaseState):
        api_client = state.get("app_context")
        squad = InstitucionalSoldiers(api_client).get_all_soldiers()
        builder = SargentoGraphBuilder(squad, squad_name="Gestión Institucional")
        return builder.build_graph()

    print("✅ Doctrina DEAA-V2.1 aplicada: Sargento de Gestión Institucional listo para el despliegue.")
    return build_sargento_agent
