from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from turismo_app.tools.herramientas_transporte import TransporteSoldiers
from turismo_app.tools.herramientas_generales import GeneralesSoldiers

def get_gestion_transporte_sargento_graph():
    """
    Construye y devuelve el agente Sargento de Gestión de Transporte.
    """
    def build_sargento_agent(state: SargentoBaseState):
        api_client = state.get("app_context")

        transporte_squad = TransporteSoldiers(api_client).get_all_soldiers()
        generales_squad = GeneralesSoldiers(api_client).get_all_soldiers()
        full_squad = transporte_squad + generales_squad

        builder = SargentoGraphBuilder(full_squad, squad_name="Gestión de Transporte")
        return builder.build_graph()

    print("✅ Doctrina DEAA-V2.1 aplicada: Sargento de Gestión de Transporte listo para el despliegue.")
    return build_sargento_agent
