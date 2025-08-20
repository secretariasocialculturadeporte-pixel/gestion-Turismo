from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from turismo_app.tools.herramientas_agencia_viaje import AgenciaViajeSoldiers
from turismo_app.tools.herramientas_generales import GeneralesSoldiers

def get_gestion_agencia_sargento_graph():
    """
    Construye y devuelve el agente Sargento de Gestión de Agencia de Viajes.
    """
    def build_sargento_agent(state: SargentoBaseState):
        api_client = state.get("app_context")

        agencia_squad = AgenciaViajeSoldiers(api_client).get_all_soldiers()
        generales_squad = GeneralesSoldiers(api_client).get_all_soldiers()
        full_squad = agencia_squad + generales_squad

        builder = SargentoGraphBuilder(full_squad, squad_name="Gestión de Agencia de Viajes")
        return builder.build_graph()

    print("✅ Doctrina DEAA-V2.1 aplicada: Sargento de Gestión de Agencia de Viajes listo para el despliegue.")
    return build_sargento_agent
