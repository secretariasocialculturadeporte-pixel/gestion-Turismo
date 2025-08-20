from typing import TypedDict, List
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from .platoons.deportes_teniente import get_deportes_lieutenant_graph

llm = ChatOpenAI(model="gpt-4o", temperature=0, model_kwargs={"response_format": {"type": "json_object"}})

class DeportesPlatoonTask(BaseModel):
    task_description: str = Field(description="La descripción detallada de la misión para el Teniente de Deportes.")
    responsible_lieutenant: str = Field(description="Debe ser 'Deportes'.")

class DeportesPlatoonPlan(BaseModel):
    plan: List[DeportesPlatoonTask]

class OperacionesDeportesCaptainState(TypedDict):
    coronel_order: str
    platoon_plan: DeportesPlatoonPlan | None
    task_queue: List[DeportesPlatoonTask]
    completed_missions: list
    final_report: str
    error: str | None

deportes_agent = get_deportes_lieutenant_graph()

async def create_platoon_plan(state: OperacionesDeportesCaptainState) -> OperacionesDeportesCaptainState:
    print("--- 🧠 CAP. OPERACIONES DEPORTIVAS: Creando Plan de Pelotón... ---")
    # Como solo hay un teniente, el plan es una delegación directa.
    # En un escenario más complejo, aquí iría un LLM para descomponer la tarea.
    plan = DeportesPlatoonPlan(plan=[
        DeportesPlatoonTask(task_description=state['coronel_order'], responsible_lieutenant='Deportes')
    ])
    state.update({"platoon_plan": plan, "task_queue": plan.plan.copy(), "completed_missions": []})
    return state

def route_to_lieutenant(state: OperacionesDeportesCaptainState):
    if state.get("error") or not state["task_queue"]:
        return "compile_report"
    return "deportes_lieutenant"

async def deportes_node(state: OperacionesDeportesCaptainState) -> OperacionesDeportesCaptainState:
    mission = state["task_queue"].pop(0)
    print(f"--- 🔽 CAPITÁN: Delegando a TTE. DEPORTES -> '{mission.task_description}' ---")
    result = await deportes_agent.ainvoke({"captain_order": mission.task_description})
    state["completed_missions"].append({"lieutenant": "Deportes", "report": result.get("final_report", "Sin reporte.")})
    return state

async def compile_final_report(state: OperacionesDeportesCaptainState) -> OperacionesDeportesCaptainState:
    report_body = "\n".join([f"- Reporte del Tte. de {m['lieutenant']}: {m['report']}" for m in state["completed_missions"]])
    state["final_report"] = f"Misión de Operaciones Deportivas completada. Resumen:\n{report_body}"
    return state

def get_operaciones_deportes_captain_graph():
    workflow = StateGraph(OperacionesDeportesCaptainState)
    workflow.add_node("planner", create_platoon_plan)
    workflow.add_node("deportes_lieutenant", deportes_node)
    workflow.add_node("compiler", compile_final_report)

    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "deportes_lieutenant")
    workflow.add_edge("deportes_lieutenant", "compiler")
    workflow.add_edge("compiler", END)

    memory = SqliteSaver.from_conn_string(":memory:")
    return workflow.compile(checkpointer=memory)
