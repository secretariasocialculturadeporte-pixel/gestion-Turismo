from typing import TypedDict, Any
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from .squads.gestion_agencia_sargento import get_gestion_agencia_sargento_graph

class GestionAgenciaLieutenantState(TypedDict):
    captain_order: str
    app_context: Any
    final_report: str
    error: str | None

gestion_agencia_sargento_builder = get_gestion_agencia_sargento_graph()

async def delegate_to_sargento(state: GestionAgenciaLieutenantState) -> GestionAgenciaLieutenantState:
    order = state['captain_order']
    print(f"--- 🫡 TENIENTE DE GESTIÓN DE AGENCIA: Recibida orden. Delegando a Sargento -> '{order}' ---")
    try:
        sargento_executor = gestion_agencia_sargento_builder(state)
        result = await sargento_executor.ainvoke({
            "teniente_order": order,
            "app_context": state['app_context']
        })
        state["final_report"] = result.get("final_report", "El Sargento de Agencia de Viajes completó la misión sin reporte.")
    except Exception as e:
        state["error"] = f"Misión de Agencia de Viajes fallida. Razón: {e}"
    return state

async def compile_report(state: GestionAgenciaLieutenantState) -> GestionAgenciaLieutenantState:
    if state.get("error"):
        state["final_report"] = state["error"]
    return state

def get_gestion_agencia_lieutenant_graph():
    workflow = StateGraph(GestionAgenciaLieutenantState)
    workflow.add_node("delegate_mission", delegate_to_sargento)
    workflow.add_node("compile_report", compile_report)
    workflow.set_entry_point("delegate_mission")
    workflow.add_edge("delegate_mission", "compile_report")
    workflow.add_edge("compile_report", END)
    memory = SqliteSaver.from_conn_string(":memory:")
    return workflow.compile(checkpointer=memory)
