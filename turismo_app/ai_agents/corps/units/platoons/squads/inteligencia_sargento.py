from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from turismo_app.tools.herramientas_inteligencia import InteligenciaSoldiers

def get_inteligencia_sargento_graph():
    """
    Construye y devuelve el agente Sargento de Inteligencia.
    """
    def build_sargento_agent(state: SargentoBaseState):
        api_client = state.get("app_context")
        squad = InteligenciaSoldiers(api_client).get_all_soldiers()
        builder = SargentoGraphBuilder(squad, squad_name="Inteligencia y Apoyo")
        return builder.build_graph()

    print("✅ Doctrina DEAA-V2.1 aplicada: Sargento de Inteligencia listo para el despliegue.")
    return build_sargento_agent
