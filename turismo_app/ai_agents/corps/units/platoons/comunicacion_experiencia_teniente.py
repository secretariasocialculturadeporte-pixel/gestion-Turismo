from typing import TypedDict, Any, List
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_openai import ChatOpenAI
from langchain_core.pydantic_v1 import BaseModel, Field
from .squads.comunicaciones_sargento import get_comunicaciones_sargento_graph
from .squads.experiencia_sargento import get_experiencia_sargento_graph

llm = ChatOpenAI(model="gpt-4o", temperature=0, model_kwargs={"response_format": {"type": "json_object"}})

class SargentoMission(BaseModel):
    task_description: str
    responsible_sargento: str = Field(description="Debe ser 'Comunicaciones' o 'Experiencia'.")

class MissionPlan(BaseModel):
    plan: List[SargentoMission]

class CommsExpLieutenantState(TypedDict):
    captain_order: str
    app_context: Any
    mission_plan: MissionPlan | None
    task_queue: List[SargentoMission]
    completed_missions: list
    final_report: str
    error: str | None

comunicaciones_sargento_builder = get_comunicaciones_sargento_graph()
experiencia_sargento_builder = get_experiencia_sargento_graph()

async def planner_node(state: CommsExpLieutenantState) -> CommsExpLieutenantState:
    print("--- 🤔 TTE. COMMS/EXP: Creando Plan de Pelotón... ---")
    planner = llm.with_structured_output(MissionPlan)
    prompt = f"""
Eres un Teniente de Comunicación y Experiencia. Descompón la orden del Capitán en misiones para tus Sargentos.
Sargentos Disponibles:
- 'Comunicaciones': Experto en notificaciones, recordatorios y mensajería.
- 'Experiencia': Experto en traducciones (MILA), accesibilidad y UX.
Orden: "{state['captain_order']}"
"""
    plan = await planner.ainvoke(prompt)
    state.update({"mission_plan": plan, "task_queue": plan.plan.copy(), "completed_missions": []})
    return state

def router_node(state: CommsExpLieutenantState):
    if not state.get("task_queue"):
        return "compiler"
    sargento = state["task_queue"][0].responsible_sargento
    if sargento == "Comunicaciones":
        return "comunicaciones_lieutenant_node"
    if sargento == "Experiencia":
        return "experiencia_lieutenant_node"
    return "router"

async def comunicaciones_lieutenant_node(state: CommsExpLieutenantState) -> CommsExpLieutenantState:
    mission = state["task_queue"].pop(0)
    sargento_executor = comunicaciones_sargento_builder(state)
    result = await sargento_executor.ainvoke({"teniente_order": mission.task_description, "app_context": state.get("app_context")})
    state["completed_missions"].append(f"Reporte del Sgto. Comunicaciones: {result.get('final_report', 'Sin reporte.')}")
    return state

async def experiencia_lieutenant_node(state: CommsExpLieutenantState) -> CommsExpLieutenantState:
    mission = state["task_queue"].pop(0)
    sargento_executor = experiencia_sargento_builder(state)
    result = await sargento_executor.ainvoke({"teniente_order": mission.task_description, "app_context": state.get("app_context")})
    state["completed_missions"].append(f"Reporte del Sgto. Experiencia: {result.get('final_report', 'Sin reporte.')}")
    return state

async def compiler_node(state: CommsExpLieutenantState) -> CommsExpLieutenantState:
    state["final_report"] = "Misión completada. Resumen: " + " | ".join(state["completed_missions"])
    return state

def get_comunicacion_experiencia_lieutenant_graph():
    workflow = StateGraph(CommsExpLieutenantState)
    workflow.add_node("planner", planner_node)
    workflow.add_node("router", lambda s: s)
    workflow.add_node("comunicaciones_lieutenant_node", comunicaciones_lieutenant_node)
    workflow.add_node("experiencia_lieutenant_node", experiencia_lieutenant_node)
    workflow.add_node("compiler", compiler_node)

    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "router")
    workflow.add_conditional_edges("router", router_node, {
        "comunicaciones_lieutenant_node": "comunicaciones_lieutenant_node",
        "experiencia_lieutenant_node": "experiencia_lieutenant_node",
        "compiler": "compiler",
        "router": "router"
    })
    workflow.add_edge("comunicaciones_lieutenant_node", "router")
    workflow.add_edge("experiencia_lieutenant_node", "router")
    workflow.add_edge("compiler", END)

    memory = SqliteSaver.from_conn_string(":memory:")
    return workflow.compile(checkpointer=memory)
