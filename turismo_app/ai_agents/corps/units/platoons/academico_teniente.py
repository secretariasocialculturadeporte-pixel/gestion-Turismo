from typing import TypedDict, Any
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from .squads.academico_sargento import get_academico_sargento_graph

class AcademicoLieutenantState(TypedDict):
    captain_order: str
    app_context: Any # Contiene la API y sesión de DB
    final_report: str
    error: str | None

# Puesto de Mando del Teniente: Instancia de su Sargento
academico_sargento_agent = get_academico_sargento_graph()

# Nodos del Grafo Supervisor del Teniente
async def delegate_to_sargento(state: AcademicoLieutenantState) -> AcademicoLieutenantState:
    """(NODO ÚNICO DE EJECUCIÓN) Delega la misión completa al Sargento especialista."""
    print(f"--- 🫡 TENIENTE ACADÉMICO: Recibida orden. Delegando al Sargento Académico -> '{state['captain_order']}' ---")
    try:
        # El Teniente confía en su Sargento para planificar y ejecutar las tareas de bajo nivel.
        # La función del sargento devuelve un constructor, que se invoca con el estado actual.
        sargento_executor = academico_sargento_agent(state)
        result = await sargento_executor.ainvoke({
            "teniente_order": state['captain_order'],
            "app_context": state['app_context']
        })
        state["final_report"] = result.get("final_report", "El Sargento completó la misión sin un reporte detallado.")
    except Exception as e:
        print(f"--- ❌ TENIENTE ACADÉMICO: El Sargento reportó un error crítico: {e} ---")
        state["error"] = f"Misión fallida bajo el mando del Sargento Académico. Razón: {e}"
    return state

async def compile_report(state: AcademicoLieutenantState) -> AcademicoLieutenantState:
    """Compila el informe final para el Capitán."""
    if state.get("error"):
        state["final_report"] = state["error"]
    print("--- 📄 TENIENTE ACADÉMICO: Informe para el Capitán listo. ---")
    return state

# Ensamblaje del Grafo Supervisor del Teniente
def get_academico_lieutenant_graph():
    workflow = StateGraph(AcademicoLieutenantState)
    workflow.add_node("delegate_mission", delegate_to_sargento)
    workflow.add_node("compile_report", compile_report)
    workflow.set_entry_point("delegate_mission")
    workflow.add_edge("delegate_mission", "compile_report")
    workflow.add_edge("compile_report", END)
    memory = SqliteSaver.from_conn_string(":memory:")
    return workflow.compile(checkpointer=memory)
