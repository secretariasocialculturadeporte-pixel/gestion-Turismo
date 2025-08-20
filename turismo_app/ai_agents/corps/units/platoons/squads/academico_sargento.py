from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from turismo_app.tools.herramientas_academico import AcademicoSoldiers

def get_academico_sargento_graph():
    """
    Construye y devuelve el agente Sargento Académico.
    Este Sargento recibe misiones de su Teniente y utiliza a su escuadra de
    Soldados para ejecutar operaciones académicas.
    """
    def build_sargento_agent(state: SargentoBaseState):
        """Función interna que construye el grafo con el contexto adecuado."""
        # En un escenario real, aquí se pasaría la conexión a la BD o el cliente de API
        # desde el app_context. Para este ejemplo, es None.
        api_client = state.get("app_context")

        # El Sargento recluta a su escuadra de soldados especialistas
        squad = AcademicoSoldiers(api_client).get_all_soldiers()

        # Construye el grafo de mando usando la plantilla estandarizada
        builder = SargentoGraphBuilder(squad, squad_name="Académico")
        return builder.build_graph()

    print("✅ Doctrina DEAA-V2.1 aplicada: Sargento Académico listo para el despliegue.")

    # Se devuelve la función constructora, no el grafo directamente.
    return build_sargento_agent
