from typing import TypedDict, List
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from .platoons.academico_teniente import get_academico_lieutenant_graph
from .platoons.comunicacion_experiencia_teniente import get_comunicacion_experiencia_lieutenant_graph
from .platoons.gamificacion_teniente import get_gamificacion_lieutenant_graph

llm = ChatOpenAI(model="gpt-4o", temperature=0, model_kwargs={"response_format": {"type": "json_object"}})

class GuiasTask(BaseModel):
    task_description: str = Field(description="La descripción detallada de la misión para el Teniente.")
    responsible_lieutenant: str = Field(description="Debe ser uno de: 'Academico', 'ComunicacionExperiencia', 'Gamificacion'.")

class GuiasPlan(BaseModel):
    plan: List[GuiasTask]

class GuiasCaptainState(TypedDict):
    coronel_order: str
    platoon_plan: GuiasPlan | None
    task_queue: List[GuiasTask]
    completed_missions: list
    final_report: str
    error: str | None

academico_agent = get_academico_lieutenant_graph()
comunicacion_agent = get_comunicacion_experiencia_lieutenant_graph()
gamificacion_agent = get_gamificacion_lieutenant_graph()

async def create_platoon_plan(state: GuiasCaptainState) -> GuiasCaptainState:
    print("--- 🧠 CAP. GUÍAS TURÍSTICOS: Creando Plan de Pelotón... ---")
    structured_llm = llm.with_structured_output(GuiasPlan)
    prompt = f"""
Eres el Capitán al mando del área de Guías Turísticos. Tu Coronel te ha dado una orden. Descompónla en un plan para tus Tenientes.
Tenientes bajo tu mando:
- 'Academico': Experto en la formación, certificación y asignación de guías a cursos.
- 'ComunicacionExperiencia': Experto en la comunicación con los guías, gestión de perfiles y feedback de los turistas.
- 'Gamificacion': Experto en el sistema de puntos, medallas y rankings para motivar a los guías y usuarios.
Analiza la orden y genera el plan en formato JSON: "{state['coronel_order']}"
"""
    plan = await structured_llm.ainvoke(prompt)
    state.update({"platoon_plan": plan, "task_queue": plan.plan.copy(), "completed_missions": []})
    return state

def route_to_lieutenant(state: GuiasCaptainState):
    if not state["task_queue"]: return "compile_report"
    lieutenant = state["task_queue"][0].responsible_lieutenant
    if lieutenant == 'Academico': return "academico_lieutenant"
    if lieutenant == 'ComunicacionExperiencia': return "comunicacion_lieutenant"
    if lieutenant == 'Gamificacion': return "gamificacion_lieutenant"
    return "route_to_lieutenant"

async def gamificacion_node(state: GuiasCaptainState) -> GuiasCaptainState:
    mission = state["task_queue"].pop(0)
    result = await gamificacion_agent.ainvoke({"captain_order": mission.task_description})
    state["completed_missions"].append({"lieutenant": "Gamificación", "report": result.get("final_report", "Sin reporte.")})
    return state

async def academico_node(state: GuiasCaptainState) -> GuiasCaptainState:
    mission = state["task_queue"].pop(0)
    result = await academico_agent.ainvoke({"captain_order": mission.task_description})
    state["completed_missions"].append({"lieutenant": "Académico", "report": result.get("final_report", "Sin reporte.")})
    return state

async def comunicacion_node(state: GuiasCaptainState) -> GuiasCaptainState:
    mission = state["task_queue"].pop(0)
    result = await comunicacion_agent.ainvoke({"captain_order": mission.task_description})
    state["completed_missions"].append({"lieutenant": "Comunicación y Exp.", "report": result.get("final_report", "Sin reporte.")})
    return state

async def compile_final_report(state: GuiasCaptainState) -> GuiasCaptainState:
    report_body = "\n".join([f"- Reporte del Tte. de {m['lieutenant']}: {m['report']}" for m in state["completed_missions"]])
    state["final_report"] = f"Misión del área de Guías Turísticos completada.\nResumen:\n{report_body}"
    return state

def get_guias_captain_graph():
    workflow = StateGraph(GuiasCaptainState)
    workflow.add_node("planner", create_platoon_plan)
    workflow.add_node("router", lambda s: s)
    workflow.add_node("academico_lieutenant", academico_node)
    workflow.add_node("comunicacion_lieutenant", comunicacion_node)
    workflow.add_node("gamificacion_lieutenant", gamificacion_node)
    workflow.add_node("compiler", compile_final_report)

    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "router")
    workflow.add_conditional_edges("router", route_to_lieutenant, {
        "academico_lieutenant": "academico_lieutenant",
        "comunicacion_lieutenant": "comunicacion_lieutenant",
        "gamificacion_lieutenant": "gamificacion_lieutenant",
        "compile_report": "compiler"
    })
    workflow.add_edge("academico_lieutenant", "router")
    workflow.add_edge("comunicacion_lieutenant", "router")
    workflow.add_edge("gamificacion_lieutenant", "router")
    workflow.add_edge("compiler", END)

    memory = SqliteSaver.from_conn_string(":memory:")
    return workflow.compile(checkpointer=memory)
