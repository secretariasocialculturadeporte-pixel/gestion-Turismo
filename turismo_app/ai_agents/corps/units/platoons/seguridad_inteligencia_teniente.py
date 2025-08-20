from typing import TypedDict, Any, List
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.pydantic_v1 import BaseModel, Field
from langgraph.checkpoint.sqlite import SqliteSaver
from .squads.seguridad_sargento import get_seguridad_sargento_graph
from .squads.inteligencia_sargento import get_inteligencia_sargento_graph

llm = ChatOpenAI(model="gpt-4o", temperature=0, model_kwargs={"response_format": {"type": "json_object"}})

class SargentoMission(BaseModel):
    task_description: str = Field(description="La descripción específica de la misión para el Sargento.")
    responsible_sargento: str = Field(description="El Sargento especialista responsable. Debe ser uno de: 'Seguridad', 'Inteligencia'.")

class MissionPlan(BaseModel):
    plan: List[SargentoMission]

class SecurityIntelligenceState(TypedDict):
    captain_order: str
    app_context: Any
    mission_plan: MissionPlan | None
    task_queue: List[SargentoMission]
    completed_missions: list
    final_report: str
    error: str | None

seguridad_sargento_builder = get_seguridad_sargento_graph()
inteligencia_sargento_builder = get_inteligencia_sargento_graph()

async def planner_node(state: SecurityIntelligenceState) -> SecurityIntelligenceState:
    print(f"--- 🤔 TENIENTE DE SEGURIDAD E INTELIGENCIA: Creando Plan de Pelotón para '{state['captain_order']}' ---")
    planner = llm.with_structured_output(MissionPlan)
    prompt = f"""
Eres un Teniente de Seguridad e Inteligencia de Datos. Descompón la orden de tu Capitán en misiones secuenciales para tus Sargentos.
Sargentos Disponibles y sus especialidades:
- 'Seguridad': Experto en login, RBAC, auditoría de acciones (STAR) y seguridad multi-inquilino.
- 'Inteligencia': Experto en analítica (KPIs), dashboards y el agente de IA para soporte.
Analiza la orden y crea el plan JSON: "{state['captain_order']}"
"""
    try:
        plan = await planner.ainvoke(prompt)
        print(f"--- ✔️ TENIENTE SEG/INT: Plan de {len(plan.plan)} pasos generado. ---")
        state.update({"mission_plan": plan, "task_queue": plan.plan.copy(), "completed_missions": []})
        return state
    except Exception as e:
        state["error"] = f"El Teniente no pudo crear un plan: {e}"; return state

def router_node(state: SecurityIntelligenceState):
    if state.get("error") or not state.get("task_queue"):
        return "compiler"
    sargento_unit = state["task_queue"][0].responsible_sargento
    if sargento_unit == "Seguridad":
        return "seguridad_sargento"
    if sargento_unit == "Inteligencia":
        return "inteligencia_sargento"
    state["task_queue"].pop(0); return "router"

async def seguridad_node(state: SecurityIntelligenceState) -> SecurityIntelligenceState:
    mission = state["task_queue"].pop(0)
    sargento_executor = seguridad_sargento_builder(state)
    result = await sargento_executor.ainvoke({"teniente_order": mission.task_description, "app_context": state["app_context"]})
    state["completed_missions"].append(f"Reporte del Sgto. de Seguridad: {result['final_report']}")
    return state

async def inteligencia_node(state: SecurityIntelligenceState) -> SecurityIntelligenceState:
    mission = state["task_queue"].pop(0)
    sargento_executor = inteligencia_sargento_builder(state)
    result = await sargento_executor.ainvoke({"teniente_order": mission.task_description, "app_context": state["app_context"]})
    state["completed_missions"].append(f"Reporte del Sgto. de Inteligencia: {result['final_report']}")
    return state

async def compiler_node(state: SecurityIntelligenceState) -> SecurityIntelligenceState:
    state["final_report"] = "Misión de Seguridad e Inteligencia completada.\n- " + "\n- ".join(state["completed_missions"])
    return state

def get_seguridad_inteligencia_lieutenant_graph():
    workflow = StateGraph(SecurityIntelligenceState)
    workflow.add_node("planner", planner_node)
    workflow.add_node("router", lambda s: s)
    workflow.add_node("seguridad_sargento", seguridad_node)
    workflow.add_node("inteligencia_sargento", inteligencia_node)
    workflow.add_node("compiler", compiler_node)

    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "router")
    workflow.add_conditional_edges("router", router_node, {
        "seguridad_sargento": "seguridad_sargento",
        "inteligencia_sargento": "inteligencia_sargento",
        "compiler": "compiler",
        "router": "router"
    })
    workflow.add_edge("seguridad_sargento", "router")
    workflow.add_edge("inteligencia_sargento", "router")
    workflow.add_edge("compiler", END)

    memory = SqliteSaver.from_conn_string(":memory:")
    return workflow.compile(checkpointer=memory)
