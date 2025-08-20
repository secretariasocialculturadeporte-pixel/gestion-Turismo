from typing import TypedDict, List
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from .units.operaciones_academicas_captain import get_operaciones_academicas_captain_graph
from .units.estrategia_plataforma_captain import get_estrategia_plataforma_captain_graph

llm = ChatOpenAI(model="gpt-4o", temperature=0, model_kwargs={"response_format": {"type": "json_object"}})

class TacticalTask(BaseModel):
    task_description: str = Field(description="La descripción específica y detallada de la misión para el Capitán.")
    responsible_captain: str = Field(description="El Capitán especialista responsable. Debe ser uno de: 'OperacionesAcademicas', 'EstrategiaPlataforma'.")

class TacticalPlan(BaseModel):
    plan: List[TacticalTask] = Field(description="La lista de misiones tácticas secuenciales para cumplir la orden del General.")

class FormacionCulturaColonelState(TypedDict):
    general_order: str
    tactical_plan: TacticalPlan | None
    task_queue: List[TacticalTask]
    completed_missions: list
    final_report: str
    error: str | None

operaciones_academicas_agent = get_operaciones_academicas_captain_graph()
estrategia_plataforma_agent = get_estrategia_plataforma_captain_graph()

async def create_tactical_plan(state: FormacionCulturaColonelState) -> FormacionCulturaColonelState:
    print("--- 🧠 CORONEL FORMACIÓN Y CULTURA: Creando Plan Táctico... ---")
    structured_llm = llm.with_structured_output(TacticalPlan)
    prompt = f"""
Eres un Coronel del Cuerpo de Formación y Cultura. Tu General te ha dado una orden estratégica. Tu deber es descomponer esta orden en un plan táctico coherente, asignando cada misión a tu Capitán especialista.
Capitanes bajo tu mando:
- 'OperacionesAcademicas': Responsable de la ejecución del día a día. Comanda a los Tenientes de Actividades Académicas, Comunicación y Gamificación. Asigna misiones relacionadas con la creación de clases, inscripciones, notificaciones, eventos y motivación estudiantil.
- 'EstrategiaPlataforma': Responsable de la infraestructura, seguridad y crecimiento. Comanda a los Tenientes de Seguridad, Inteligencia de Datos y Expansión Institucional. Asigna misiones relacionadas con la creación de nuevas sedes (inquilinos), auditorías de seguridad, generación de analíticas y administración del personal.
Analiza la siguiente orden del General y genera el plan táctico en formato JSON: "{state['general_order']}"
"""
    try:
        plan = await structured_llm.ainvoke(prompt)
        print(f"--- 📝 CORONEL FORMACIÓN Y CULTURA: Plan Táctico Generado. Pasos: {len(plan.plan)} ---")
        for i, task in enumerate(plan.plan):
            print(f" Paso {i+1}: Delegado a [{task.responsible_captain}] -> {task.task_description}")
        state.update({
            "tactical_plan": plan,
            "task_queue": plan.plan.copy(),
            "completed_missions": [],
            "error": None
        })
        return state
    except Exception as e:
        print(f"--- ❌ CORONEL FORMACIÓN Y CULTURA: Error crítico al planificar: {e} ---")
        state["error"] = "No se pudo interpretar la orden para crear un plan táctico."
        return state

def route_to_captain(state: FormacionCulturaColonelState):
    if state.get("error"): return "compile_report"
    if not state["task_queue"]:
        print("--- ✅ CORONEL FORMACIÓN Y CULTURA: Todas las misiones del plan completadas. ---")
        return "compile_report"

    next_mission = state["task_queue"][0]
    captain_unit = next_mission.responsible_captain
    print(f"--- routing.py CORONEL FORMACIÓN Y CULTURA: Enrutando misión a Capitán '{captain_unit}' ---")

    if captain_unit == 'OperacionesAcademicas': return "operaciones_academicas_captain"
    elif captain_unit == 'EstrategiaPlataforma': return "estrategia_plataforma_captain"
    else:
        print(f"--- ⚠️ CORONEL FORMACIÓN Y CULTURA: Capitán desconocido '{captain_unit}'. Misión abortada. ---")
        state["error"] = f"Planificación defectuosa: Se intentó delegar a una unidad desconocida '{captain_unit}'."
        state["task_queue"].pop(0)
        return "route_to_captain"

async def operaciones_academicas_node(state: FormacionCulturaColonelState) -> FormacionCulturaColonelState:
    mission = state["task_queue"].pop(0)
    print(f"--- 🔽 CORONEL: Delegando a CAP. OPERACIONES ACADÉMICAS -> '{mission.task_description}' ---")
    result = await operaciones_academicas_agent.ainvoke({"coronel_order": mission.task_description})
    state["completed_missions"].append({
        "captain": "Operaciones Academicas",
        "mission": mission.task_description,
        "report": result.get("final_report", "Sin reporte.")
    })
    return state

async def estrategia_plataforma_node(state: FormacionCulturaColonelState) -> FormacionCulturaColonelState:
    mission = state["task_queue"].pop(0)
    print(f"--- 🔽 CORONEL: Delegando a CAP. ESTRATEGIA Y PLATAFORMA -> '{mission.task_description}' ---")
    result = await estrategia_plataforma_agent.ainvoke({"coronel_order": mission.task_description})
    state["completed_missions"].append({
        "captain": "Estrategia y Plataforma",
        "mission": mission.task_description,
        "report": result.get("final_report", "Sin reporte.")
    })
    return state

async def compile_final_report(state: FormacionCulturaColonelState) -> FormacionCulturaColonelState:
    print("--- 📄 CORONEL FORMACIÓN Y CULTURA: Compilando Informe de División para el General... ---")
    if state.get("error"):
        state["final_report"] = f"Misión de la División fallida. Razón: {state['error']}"
        return state

    report_body = "\n".join(
        [f"- Reporte del Capitán de {m['captain']}:\n Misión: '{m['mission']}'\n Resultado: {m['report']}" for m in state["completed_missions"]]
    )
    state["final_report"] = f"Misión de la División de Formación y Cultura completada.\nResumen de Operaciones:\n{report_body}"
    return state

def get_formacion_cultura_colonel_graph():
    workflow = StateGraph(FormacionCulturaColonelState)
    workflow.add_node("planner", create_tactical_plan)
    workflow.add_node("router", lambda state: state)
    workflow.add_node("operaciones_academicas_captain", operaciones_academicas_node)
    workflow.add_node("estrategia_plataforma_captain", estrategia_plataforma_node)
    workflow.add_node("compiler", compile_final_report)

    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "router")
    workflow.add_conditional_edges(
        "router",
        route_to_captain,
        {
            "operaciones_academicas_captain": "operaciones_academicas_captain",
            "estrategia_plataforma_captain": "estrategia_plataforma_captain",
            "compile_report": "compiler"
        }
    )
    workflow.add_edge("operaciones_academicas_captain", "router")
    workflow.add_edge("estrategia_plataforma_captain", "router")
    workflow.add_edge("compiler", END)

    memory = SqliteSaver.from_conn_string(":memory:")
    return workflow.compile(checkpointer=memory)
