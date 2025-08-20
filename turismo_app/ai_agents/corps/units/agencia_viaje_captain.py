from typing import TypedDict, List
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from .platoons.gestion_agencia_teniente import get_gestion_agencia_lieutenant_graph

llm = ChatOpenAI(model="gpt-4o", temperature=0, model_kwargs={"response_format": {"type": "json_object"}})

class AgenciaTask(BaseModel):
    task_description: str = Field(description="La descripción detallada de la misión para el Teniente de Agencia de Viaje.")
    responsible_lieutenant: str = Field(description="Debe ser 'GestionAgencia'.")

class AgenciaPlan(BaseModel):
    plan: List[AgenciaTask]

class AgenciaCaptainState(TypedDict):
    coronel_order: str
    platoon_plan: AgenciaPlan | None
    task_queue: List[AgenciaTask]
    completed_missions: list
    final_report: str
    error: str | None

gestion_agencia_agent = get_gestion_agencia_lieutenant_graph()

async def create_platoon_plan(state: AgenciaCaptainState) -> AgenciaCaptainState:
    print("--- 🧠 CAP. AGENCIAS DE VIAJE: Creando Plan de Pelotón... ---")
    plan = AgenciaPlan(plan=[
        AgenciaTask(task_description=state['coronel_order'], responsible_lieutenant='GestionAgencia')
    ])
    state.update({"platoon_plan": plan, "task_queue": plan.plan.copy(), "completed_missions": []})
    return state

def route_to_lieutenant(state: AgenciaCaptainState):
    if not state["task_queue"]: return "compile_report"
    return "gestion_agencia_lieutenant"

async def lieutenant_node(state: AgenciaCaptainState) -> AgenciaCaptainState:
    mission = state["task_queue"].pop(0)
    print(f"--- 🔽 CAPITÁN (Agencia): Delegando a TTE. GESTION AGENCIA -> '{mission.task_description}' ---")
    result = await gestion_agencia_agent.ainvoke({"captain_order": mission.task_description, "app_context": state.get("app_context")})
    state["completed_missions"].append({"lieutenant": "GestionAgencia", "report": result.get("final_report", "Misión de agencia de viaje completada.")})
    return state

async def compile_final_report(state: AgenciaCaptainState) -> AgenciaCaptainState:
    report_body = "\n".join([f"- Reporte del Tte. de {m['lieutenant']}: {m['report']}" for m in state["completed_missions"]])
    state["final_report"] = f"Misión del área de Agencias de Viaje completada.\nResumen:\n{report_body}"
    return state

def get_agencia_viaje_captain_graph():
    workflow = StateGraph(AgenciaCaptainState)
    workflow.add_node("planner", create_platoon_plan)
    workflow.add_node("gestion_agencia_lieutenant", lieutenant_node)
    workflow.add_node("compiler", compile_final_report)

    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "gestion_agencia_lieutenant")
    workflow.add_edge("gestion_agencia_lieutenant", "compiler")
    workflow.add_edge("compiler", END)

    memory = SqliteSaver.from_conn_string(":memory:")
    return workflow.compile(checkpointer=memory)
