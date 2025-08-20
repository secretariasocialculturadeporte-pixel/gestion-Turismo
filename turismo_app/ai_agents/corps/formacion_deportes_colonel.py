from typing import TypedDict, List
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from .units.operaciones_deportes_captain import get_operaciones_deportes_captain_graph

llm = ChatOpenAI(model="gpt-4o", temperature=0, model_kwargs={"response_format": {"type": "json_object"}})

class TacticalTask(BaseModel):
    task_description: str = Field(description="La descripción específica y detallada de la misión para el Capitán de Deportes.")
    responsible_captain: str = Field(description="Debe ser 'OperacionesDeportivas'.")

class TacticalPlan(BaseModel):
    plan: List[TacticalTask]

class FormacionDeportesColonelState(TypedDict):
    general_order: str
    tactical_plan: TacticalPlan | None
    task_queue: List[TacticalTask]
    completed_missions: list
    final_report: str
    error: str | None

operaciones_deportes_agent = get_operaciones_deportes_captain_graph()

async def create_tactical_plan(state: FormacionDeportesColonelState) -> FormacionDeportesColonelState:
    print("--- 🧠 CORONEL FORMACIÓN Y DEPORTES: Creando Plan Táctico... ---")
    # Como solo hay un capitán, el plan es una delegación directa.
    plan = TacticalPlan(plan=[
        TacticalTask(task_description=state['general_order'], responsible_captain='OperacionesDeportivas')
    ])
    state.update({
        "tactical_plan": plan,
        "task_queue": plan.plan.copy(),
        "completed_missions": [],
        "error": None
    })
    return state

def route_to_captain(state: FormacionDeportesColonelState):
    if state.get("error") or not state["task_queue"]:
        return "compile_report"
    return "operaciones_deportes_captain"

async def operaciones_deportes_node(state: FormacionDeportesColonelState) -> FormacionDeportesColonelState:
    mission = state["task_queue"].pop(0)
    print(f"--- 🔽 CORONEL: Delegando a CAP. OPERACIONES DEPORTIVAS -> '{mission.task_description}' ---")
    result = await operaciones_deportes_agent.ainvoke({"coronel_order": mission.task_description})
    state["completed_missions"].append({
        "captain": "Operaciones Deportivas",
        "mission": mission.task_description,
        "report": result.get("final_report", "Sin reporte.")
    })
    return state

async def compile_final_report(state: FormacionDeportesColonelState) -> FormacionDeportesColonelState:
    report_body = "\n".join([f"- Reporte del Capitán de {m['captain']}:\n  Misión: '{m['mission']}'\n  Resultado: {m['report']}" for m in state["completed_missions"]])
    state["final_report"] = f"Misión de la División de Formación y Deportes completada.\nResumen de Operaciones:\n{report_body}"
    return state

def get_formacion_deportes_colonel_graph():
    workflow = StateGraph(FormacionDeportesColonelState)
    workflow.add_node("planner", create_tactical_plan)
    workflow.add_node("operaciones_deportes_captain", operaciones_deportes_node)
    workflow.add_node("compiler", compile_final_report)

    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "operaciones_deportes_captain")
    workflow.add_edge("operaciones_deportes_captain", "compiler")
    workflow.add_edge("compiler", END)

    memory = SqliteSaver.from_conn_string(":memory:")
    return workflow.compile(checkpointer=memory)
