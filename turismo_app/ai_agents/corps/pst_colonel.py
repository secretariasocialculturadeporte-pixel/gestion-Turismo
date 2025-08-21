from typing import TypedDict, List
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from .units.restaurante_captain import get_restaurante_captain_graph
from .units.hotel_captain import get_hotel_captain_graph
from .units.agencia_viaje_captain import get_agencia_viaje_captain_graph
from .units.guias_captain import get_guias_captain_graph
from .units.eventos_captain import get_eventos_captain_graph
from .units.transporte_captain import get_transporte_captain_graph

llm = ChatOpenAI(model="gpt-4o", temperature=0, model_kwargs={"response_format": {"type": "json_object"}})

class PST_TacticalTask(BaseModel):
    task_description: str = Field(description="La descripción específica y detallada de la misión para el Capitán de área.")
    responsible_captain: str = Field(description="El Capitán especialista del área de PST. Debe ser uno de: 'Restaurantes', 'Hoteles', 'AgenciasViaje', 'GuiasTuristicos', 'Eventos', 'Transporte'.")

class PST_TacticalPlan(BaseModel):
    plan: List[PST_TacticalTask] = Field(description="La lista de misiones tácticas para cumplir la orden del General sobre los PST.")

class PSTColonelState(TypedDict):
    general_order: str
    tactical_plan: PST_TacticalPlan | None
    task_queue: List[PST_TacticalTask]
    completed_missions: list
    final_report: str
    error: str | None

# Instanciar todos los capitanes
captain_executors = {
    "Restaurantes": get_restaurante_captain_graph(),
    "Hoteles": get_hotel_captain_graph(),
    "AgenciasViaje": get_agencia_viaje_captain_graph(),
    "GuiasTuristicos": get_guias_captain_graph(),
    "Eventos": get_eventos_captain_graph(),
    "Transporte": get_transporte_captain_graph(),
}

async def create_tactical_plan(state: PSTColonelState) -> PSTColonelState:
    print("--- 🧠 CORONEL PST: Creando Plan Táctico... ---")
    structured_llm = llm.with_structured_output(PST_TacticalPlan)
    prompt = f"""
Eres el Coronel al mando del cuerpo de Prestadores de Servicios Turísticos (PST). Tu misión es analizar la orden del General y delegarla al Capitán del área correcta.
Capitanes bajo tu mando:
- 'Restaurantes': Gestiona todo lo relacionado con restaurantes, bares, menús, comandas y delivery.
- 'Hoteles': Gestiona todo lo relacionado con hoteles, alojamientos, reservas de habitaciones y disponibilidad.
- 'AgenciasViaje': Gestiona paquetes turísticos, reservas de tours y logística de viajes.
- 'GuiasTuristicos': Gestiona perfiles de guías, sus especialidades, y la asignación a tours.
- 'Eventos': Gestiona la creación y promoción de eventos, torneos y actividades especiales.
- 'Transporte': Gestiona la flota de vehículos, disponibilidad y reservas de transporte.

Analiza la siguiente orden del General y genera el plan táctico en formato JSON: "{state['general_order']}"
"""
    try:
        plan = await structured_llm.ainvoke(prompt)
        state.update({"tactical_plan": plan, "task_queue": plan.plan.copy(), "completed_missions": [], "error": None})
        return state
    except Exception as e:
        state["error"] = f"No se pudo crear un plan táctico: {e}"
        return state

def route_to_captain(state: PSTColonelState):
    if state.get("error") or not state["task_queue"]:
        return "compiler"

    captain_unit = state["task_queue"][0].responsible_captain
    print(f"--- CORONEL PST: Enrutando misión a Capitán '{captain_unit}' ---")

    if captain_unit in captain_executors:
        return captain_unit
    else:
        return "handle_error"

async def captain_node(state: PSTColonelState) -> PSTColonelState:
    mission = state["task_queue"].pop(0)
    captain_name = mission.responsible_captain
    captain_agent = captain_executors.get(captain_name)

    if not captain_agent:
        state["completed_missions"].append({"captain": captain_name, "mission": mission.task_description, "report": "Error: Capitán no encontrado."})
        return state

    print(f"--- 🔽 CORONEL: Delegando a CAP. {captain_name.upper()} -> '{mission.task_description}' ---")
    result = await captain_agent.ainvoke({"coronel_order": mission.task_description, "app_context": state.get("app_context")})
    state["completed_missions"].append({ "captain": captain_name, "mission": mission.task_description, "report": result.get("final_report", "Sin reporte.") })
    return state

async def handle_error_node(state: PSTColonelState) -> PSTColonelState:
    mission = state["task_queue"].pop(0)
    error_message = f"Planificación defectuosa: Se intentó delegar a un Capitán desconocido: '{mission.responsible_captain}'."
    state["completed_missions"].append({"captain": "Desconocido", "mission": mission.task_description, "report": error_message})
    return state

async def compile_final_report(state: PSTColonelState) -> PSTColonelState:
    report_body = "\n".join([f"- Reporte del Capitán de {m['captain']}:\n  Misión: '{m['mission']}'\n  Resultado: {m['report']}" for m in state["completed_missions"]])
    state["final_report"] = f"Misión del Cuerpo PST completada.\nResumen de Operaciones:\n{report_body}"
    return state

def get_pst_colonel_graph():
    workflow = StateGraph(PSTColonelState)
    workflow.add_node("planner", create_tactical_plan)
    workflow.add_node("router", lambda s: s)
    workflow.add_node("handle_error", handle_error_node)

    for captain_name in captain_executors.keys():
        workflow.add_node(captain_name, captain_node)

    workflow.add_node("compiler", compile_final_report)

    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "router")

    routing_map = {name: name for name in captain_executors.keys()}
    routing_map["handle_error"] = "handle_error"
    routing_map["compiler"] = "compiler"

    workflow.add_conditional_edges("router", route_to_captain, routing_map)

    for captain_name in captain_executors.keys():
        workflow.add_edge(captain_name, "router")
    workflow.add_edge("handle_error", "router")

    workflow.add_edge("compiler", END)

    memory = SqliteSaver.from_conn_string(":memory:")
    return workflow.compile(checkpointer=memory)
