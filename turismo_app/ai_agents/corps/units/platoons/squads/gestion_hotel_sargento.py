from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from turismo_app.tools.herramientas_hotel import HotelSoldiers
from turismo_app.tools.herramientas_generales import GeneralesSoldiers

def get_gestion_hotel_sargento_graph():
    """
    Construye y devuelve el agente Sargento de Gestión de Hotel.
    """
    def build_sargento_agent(state: SargentoBaseState):
        api_client = state.get("app_context")

        # Reclutar soldados de ambas escuadras
        hotel_squad = HotelSoldiers(api_client).get_all_soldiers()
        generales_squad = GeneralesSoldiers(api_client).get_all_soldiers()
        full_squad = hotel_squad + generales_squad

        builder = SargentoGraphBuilder(full_squad, squad_name="Gestión de Hotel")
        return builder.build_graph()

    print("✅ Doctrina DEAA-V2.1 aplicada: Sargento de Gestión de Hotel listo para el despliegue.")
    return build_sargento_agent
