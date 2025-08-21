from typing import TypedDict, List
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from .platoons.gestion_transporte_teniente import get_gestion_transporte_lieutenant_graph

llm = ChatOpenAI(model="gpt-4o", temperature=0, model_kwargs={"response_format": {"type": "json_object"}})

class TransporteTask(BaseModel):
    task_description: str = Field(description="La descripción detallada de la misión para el Teniente de Transporte.")
    responsible_lieutenant: str = Field(description="Debe ser 'GestionTransporte'.")

class TransportePlan(BaseModel):
    plan: List[TransporteTask]

class TransporteCaptainState(TypedDict):
    coronel_order: str
    platoon_plan: TransportePlan | None
    task_queue: List[TransporteTask]
    completed_missions: list
    final_report: str
    error: str | None

gestion_transporte_agent = get_gestion_transporte_lieutenant_graph()

async def create_platoon_plan(state: TransporteCaptainState) -> TransporteCaptainState:
    print("--- 🧠 CAP. TRANSPORTE: Creando Plan de Pelotón... ---")
    plan = TransportePlan(plan=[
        TransporteTask(task_description=state['coronel_order'], responsible_lieutenant='GestionTransporte')
    ])
    state.update({"platoon_plan": plan, "task_queue": plan.plan.copy(), "completed_missions": []})
    return state

def route_to_lieutenant(state: TransporteCaptainState):
    if not state["task_queue"]: return "compile_report"
    return "gestion_transporte_lieutenant"

async def lieutenant_node(state: TransporteCaptainState) -> TransporteCaptainState:
    mission = state["task_queue"].pop(0)
    print(f"--- 🔽 CAPITÁN (Transporte): Delegando a TTE. GESTION TRANSPORTE -> '{mission.task_description}' ---")
    result = await gestion_transporte_agent.ainvoke({"captain_order": mission.task_description, "app_context": state.get("app_context")})
    state["completed_missions"].append({"lieutenant": "GestionTransporte", "report": result.get("final_report", "Misión de transporte completada.")})
    return state

async def compile_final_report(state: TransporteCaptainState) -> TransporteCaptainState:
    report_body = "\n".join([f"- Reporte del Tte. de {m['lieutenant']}: {m['report']}" for m in state["completed_missions"]])
    state["final_report"] = f"Misión del área de Transporte completada.\nResumen:\n{report_body}"
    return state

def get_transporte_captain_graph():
    workflow = StateGraph(TransporteCaptainState)
    workflow.add_node("planner", create_platoon_plan)
    workflow.add_node("gestion_transporte_lieutenant", lieutenant_node)
    workflow.add_node("compiler", compile_final_report)

    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "gestion_transporte_lieutenant")
    workflow.add_edge("gestion_transporte_lieutenant", "compiler")
    workflow.add_edge("compiler", END)

    memory = SqliteSaver.from_conn_string(":memory:")
    return workflow.compile(checkpointer=memory)
