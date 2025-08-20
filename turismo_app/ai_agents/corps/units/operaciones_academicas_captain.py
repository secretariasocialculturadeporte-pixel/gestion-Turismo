from typing import TypedDict, List
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from .platoons.academico_teniente import get_academico_lieutenant_graph
from .platoons.comunicacion_experiencia_teniente import get_comunicacion_experiencia_lieutenant_graph
from .platoons.gamificacion_teniente import get_gamificacion_lieutenant_graph

llm = ChatOpenAI(model="gpt-4o", temperature=0, model_kwargs={"response_format": {"type": "json_object"}})

class PlatoonTask(BaseModel):
    task_description: str = Field(description="La descripción detallada de la misión para el Teniente.")
    responsible_lieutenant: str = Field(description="El Teniente especialista responsable. Debe ser uno de: 'Academico', 'ComunicacionExperiencia', 'Gamificacion'.")

class PlatoonPlan(BaseModel):
    plan: List[PlatoonTask] = Field(description="La lista de misiones para los Tenientes.")

class OperacionesCaptainState(TypedDict):
    coronel_order: str
    platoon_plan: PlatoonPlan | None
    task_queue: List[PlatoonTask]
    completed_missions: list
    final_report: str
    error: str | None

academico_agent = get_academico_lieutenant_graph()
comunicacion_agent = get_comunicacion_experiencia_lieutenant_graph()
gamificacion_agent = get_gamificacion_lieutenant_graph()

async def create_platoon_plan(state: OperacionesCaptainState) -> OperacionesCaptainState:
    print("--- 🧠 CAP. OPERACIONES ACADÉMICAS: Creando Plan de Pelotón... ---")
    structured_llm = llm.with_structured_output(PlatoonPlan)
    prompt = f"""
Eres un Capitán de Operaciones Académicas. Tu Coronel te ha dado una orden. Tu deber es descomponerla en un plan detallado, asignando cada misión a tu Teniente especialista.
Tenientes bajo tu mando:
- 'Academico': Comanda inscripciones, clases, asistencia, reservas e instructores.
- 'ComunicacionExperiencia': Dirige notificaciones, mensajería interna, traducciones y experiencia de usuario.
- 'Gamificacion': Orquesta el sistema de puntos, medallas y rankings.
Analiza la orden de tu Coronel y genera el plan de pelotón en formato JSON: "{state['coronel_order']}"
"""
    try:
        plan = await structured_llm.ainvoke(prompt)
        print(f"--- 📝 CAP. OPERACIONES ACADÉMICAS: Plan de Pelotón Generado. Pasos: {len(plan.plan)} ---")
        state.update({"platoon_plan": plan, "task_queue": plan.plan.copy(), "completed_missions": []})
        return state
    except Exception as e:
        state["error"] = f"No se pudo crear un plan de pelotón: {e}"; return state

def route_to_lieutenant(state: OperacionesCaptainState):
    if state.get("error") or not state["task_queue"]:
        return "compile_report"
    lieutenant_unit = state["task_queue"][0].responsible_lieutenant
    if lieutenant_unit == 'Academico': return "academico_lieutenant"
    if lieutenant_unit == 'ComunicacionExperiencia': return "comunicacion_lieutenant"
    if lieutenant_unit == 'Gamificacion': return "gamificacion_lieutenant"
    state["task_queue"].pop(0); return "route_to_lieutenant"

async def academico_node(state: OperacionesCaptainState) -> OperacionesCaptainState:
    mission = state["task_queue"].pop(0)
    print(f"--- 🔽 CAPITÁN: Delegando a TTE. ACADÉMICO -> '{mission.task_description}' ---")
    result = await academico_agent.ainvoke({"captain_order": mission.task_description})
    state["completed_missions"].append({"lieutenant": "Académico", "report": result.get("final_report", "Sin reporte.")})
    return state

async def comunicacion_node(state: OperacionesCaptainState) -> OperacionesCaptainState:
    mission = state["task_queue"].pop(0)
    print(f"--- 🔽 CAPITÁN: Delegando a TTE. COMUNICACIÓN -> '{mission.task_description}' ---")
    result = await comunicacion_agent.ainvoke({"captain_order": mission.task_description})
    state["completed_missions"].append({"lieutenant": "Comunicación y Exp.", "report": result.get("final_report", "Sin reporte.")})
    return state

async def gamificacion_node(state: OperacionesCaptainState) -> OperacionesCaptainState:
    mission = state["task_queue"].pop(0)
    print(f"--- 🔽 CAPITÁN: Delegando a TTE. GAMIFICACIÓN -> '{mission.task_description}' ---")
    result = await gamificacion_agent.ainvoke({"captain_order": mission.task_description})
    state["completed_missions"].append({"lieutenant": "Gamificación", "report": result.get("final_report", "Sin reporte.")})
    return state

async def compile_final_report(state: OperacionesCaptainState) -> OperacionesCaptainState:
    print("--- 📄 CAP. OPERACIONES ACADÉMICAS: Compilando Informe Táctico para el Coronel... ---")
    report_body = "\n".join([f"- Reporte del Tte. de {m['lieutenant']}: {m['report']}" for m in state["completed_missions"]])
    state["final_report"] = f"Misión de Operaciones Académicas completada. Resumen:\n{report_body}"
    return state

def get_operaciones_academicas_captain_graph():
    workflow = StateGraph(OperacionesCaptainState)
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
