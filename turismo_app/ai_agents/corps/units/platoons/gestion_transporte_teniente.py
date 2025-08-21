from typing import TypedDict, Any
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from .squads.gestion_transporte_sargento import get_gestion_transporte_sargento_graph

class GestionTransporteLieutenantState(TypedDict):
    captain_order: str
    app_context: Any
    final_report: str
    error: str | None

gestion_transporte_sargento_builder = get_gestion_transporte_sargento_graph()

async def delegate_to_sargento(state: GestionTransporteLieutenantState) -> GestionTransporteLieutenantState:
    order = state['captain_order']
    print(f"--- 🫡 TENIENTE DE GESTIÓN DE TRANSPORTE: Recibida orden. Delegando a Sargento -> '{order}' ---")
    try:
        sargento_executor = gestion_transporte_sargento_builder(state)
        result = await sargento_executor.ainvoke({
            "teniente_order": order,
            "app_context": state['app_context']
        })
        state["final_report"] = result.get("final_report", "El Sargento de Transporte completó la misión sin reporte.")
    except Exception as e:
        state["error"] = f"Misión de Transporte fallida. Razón: {e}"
    return state

async def compile_report(state: GestionTransporteLieutenantState) -> GestionTransporteLieutenantState:
    if state.get("error"):
        state["final_report"] = state["error"]
    return state

def get_gestion_transporte_lieutenant_graph():
    workflow = StateGraph(GestionTransporteLieutenantState)
    workflow.add_node("delegate_mission", delegate_to_sargento)
    workflow.add_node("compile_report", compile_report)
    workflow.set_entry_point("delegate_mission")
    workflow.add_edge("delegate_mission", "compile_report")
    workflow.add_edge("compile_report", END)
    memory = SqliteSaver.from_conn_string(":memory:")
    return workflow.compile(checkpointer=memory)
