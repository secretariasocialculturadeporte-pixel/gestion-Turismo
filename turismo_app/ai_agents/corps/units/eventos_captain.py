from typing import TypedDict, List
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from .platoons.gestion_eventos_teniente import get_gestion_eventos_lieutenant_graph
from .platoons.deportes_teniente import get_deportes_lieutenant_graph

llm = ChatOpenAI(model="gpt-4o", temperature=0, model_kwargs={"response_format": {"type": "json_object"}})

class EventoTask(BaseModel):
    task_description: str = Field(description="La descripción detallada de la misión para el Teniente.")
    responsible_lieutenant: str = Field(description="Debe ser uno de: 'GestionEventos', 'Deportes'.")

class EventoPlan(BaseModel):
    plan: List[EventoTask]

class EventosCaptainState(TypedDict):
    coronel_order: str
    platoon_plan: EventoPlan | None
    task_queue: List[EventoTask]
    completed_missions: list
    final_report: str
    error: str | None

gestion_eventos_agent = get_gestion_eventos_lieutenant_graph()
deportes_agent = get_deportes_lieutenant_graph()

async def create_platoon_plan(state: EventosCaptainState) -> EventosCaptainState:
    print("--- 🧠 CAP. EVENTOS: Creando Plan de Pelotón... ---")
    structured_llm = llm.with_structured_output(EventoPlan)
    prompt = f"""
Eres el Capitán al mando del área de Eventos. Tu Coronel te ha dado una orden. Descompónla en un plan para tus Tenientes.
Tenientes bajo tu mando:
- 'GestionEventos': Experto en la creación de eventos generales, culturales, y festivales.
- 'Deportes': Experto en la gestión de torneos y competiciones deportivas.
Analiza la orden y genera el plan en formato JSON: "{state['coronel_order']}"
"""
    plan = await structured_llm.ainvoke(prompt)
    state.update({"platoon_plan": plan, "task_queue": plan.plan.copy(), "completed_missions": []})
    return state

def route_to_lieutenant(state: EventosCaptainState):
    if not state["task_queue"]: return "compile_report"
    lieutenant = state["task_queue"][0].responsible_lieutenant
    if lieutenant == 'GestionEventos': return "gestion_eventos_lieutenant"
    if lieutenant == 'Deportes': return "deportes_lieutenant"
    return "route_to_lieutenant"

async def lieutenant_node_placeholder(state: EventosCaptainState) -> EventosCaptainState:
    mission = state["task_queue"].pop(0)
    lieutenant = mission.responsible_lieutenant
    print(f"--- 🔽 CAPITÁN (Eventos): Delegando a TTE. {lieutenant.upper()} -> '{mission.task_description}' ---")
    state["completed_missions"].append({"lieutenant": lieutenant, "report": f"Misión para {lieutenant} completada (simulado)."})
    return state

async def deportes_node(state: EventosCaptainState) -> EventosCaptainState:
    mission = state["task_queue"].pop(0)
    result = await deportes_agent.ainvoke({"captain_order": mission.task_description})
    state["completed_missions"].append({"lieutenant": "Deportes", "report": result.get("final_report", "Sin reporte.")})
    return state

async def compile_final_report(state: EventosCaptainState) -> EventosCaptainState:
    report_body = "\n".join([f"- Reporte del Tte. de {m['lieutenant']}: {m['report']}" for m in state["completed_missions"]])
    state["final_report"] = f"Misión del área de Eventos completada.\nResumen:\n{report_body}"
    return state

def get_eventos_captain_graph():
    workflow = StateGraph(EventosCaptainState)
    workflow.add_node("planner", create_platoon_plan)
    workflow.add_node("router", lambda s: s)
    workflow.add_node("gestion_eventos_lieutenant", lieutenant_node_placeholder)
    workflow.add_node("deportes_lieutenant", deportes_node)
    workflow.add_node("compiler", compile_final_report)

    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "router")
    workflow.add_conditional_edges("router", route_to_lieutenant, {
        "gestion_eventos_lieutenant": "gestion_eventos_lieutenant",
        "deportes_lieutenant": "deportes_lieutenant",
        "compile_report": "compiler",
        "router": "router"
    })
    workflow.add_edge("gestion_eventos_lieutenant", "router")
    workflow.add_edge("deportes_lieutenant", "router")
    workflow.add_edge("compiler", END)

    memory = SqliteSaver.from_conn_string(":memory:")
    return workflow.compile(checkpointer=memory)
