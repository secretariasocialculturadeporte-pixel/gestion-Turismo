from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from turismo_app.tools.herramientas_experiencia import ExperienciaSoldiers

def get_experiencia_sargento_graph():
    """
    Construye y devuelve el agente Sargento de Experiencia.
    """
    def build_sargento_agent(state: SargentoBaseState):
        api_client = state.get("app_context")
        squad = ExperienciaSoldiers(api_client).get_all_soldiers()
        builder = SargentoGraphBuilder(squad, squad_name="Internacionalización y UX")
        return builder.build_graph()

    print("✅ Doctrina DEAA-V2.1 aplicada: Sargento de Experiencia listo para el despliegue.")
    return build_sargento_agent
