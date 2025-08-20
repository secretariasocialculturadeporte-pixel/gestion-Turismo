from typing import TypedDict, List
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from .platoons.gestion_menu_teniente import get_gestion_menu_lieutenant_graph
from .platoons.gestion_pedidos_teniente import get_gestion_pedidos_lieutenant_graph

llm = ChatOpenAI(model="gpt-4o", temperature=0, model_kwargs={"response_format": {"type": "json_object"}})

class RestauranteTask(BaseModel):
    task_description: str = Field(description="La descripción detallada de la misión para el Teniente de Restaurante.")
    responsible_lieutenant: str = Field(description="Debe ser uno de: 'GestionMenu', 'GestionPedidos'.")

class RestaurantePlan(BaseModel):
    plan: List[RestauranteTask]

class RestauranteCaptainState(TypedDict):
    coronel_order: str
    platoon_plan: RestaurantePlan | None
    task_queue: List[RestauranteTask]
    completed_missions: list
    final_report: str
    error: str | None

# Placeholder instances - will be replaced with actual agent graphs
gestion_menu_agent = get_gestion_menu_lieutenant_graph()
gestion_pedidos_agent = get_gestion_pedidos_lieutenant_graph()

async def create_platoon_plan(state: RestauranteCaptainState) -> RestauranteCaptainState:
    print("--- 🧠 CAP. RESTAURANTES: Creando Plan de Pelotón... ---")
    structured_llm = llm.with_structured_output(RestaurantePlan)
    prompt = f"""
Eres el Capitán al mando del área de Restaurantes. Tu Coronel te ha dado una orden. Descompónla en un plan para tus Tenientes.
Tenientes bajo tu mando:
- 'GestionMenu': Experto en crear, actualizar y eliminar productos del menú.
- 'GestionPedidos': Experto en tomar, procesar y gestionar el estado de los pedidos, incluyendo delivery.
Analiza la orden y genera el plan en formato JSON: "{state['coronel_order']}"
"""
    plan = await structured_llm.ainvoke(prompt)
    state.update({"platoon_plan": plan, "task_queue": plan.plan.copy(), "completed_missions": []})
    return state

def route_to_lieutenant(state: RestauranteCaptainState):
    if not state["task_queue"]: return "compile_report"
    lieutenant = state["task_queue"][0].responsible_lieutenant
    if lieutenant == 'GestionMenu': return "gestion_menu_lieutenant"
    if lieutenant == 'GestionPedidos': return "gestion_pedidos_lieutenant"
    return "route_to_lieutenant"

async def lieutenant_node_placeholder(state: RestauranteCaptainState) -> RestauranteCaptainState:
    mission = state["task_queue"].pop(0)
    lieutenant = mission.responsible_lieutenant
    print(f"--- 🔽 CAPITÁN (Restaurante): Delegando a TTE. {lieutenant.upper()} -> '{mission.task_description}' ---")
    # En la implementación real, se invocaría al agente teniente correspondiente
    # result = await lieutenant_agent.ainvoke(...)
    state["completed_missions"].append({"lieutenant": lieutenant, "report": f"Misión para {lieutenant} completada (simulado)."})
    return state

async def compile_final_report(state: RestauranteCaptainState) -> RestauranteCaptainState:
    report_body = "\n".join([f"- Reporte del Tte. de {m['lieutenant']}: {m['report']}" for m in state["completed_missions"]])
    state["final_report"] = f"Misión del área de Restaurantes completada.\nResumen:\n{report_body}"
    return state

def get_restaurante_captain_graph():
    workflow = StateGraph(RestauranteCaptainState)
    workflow.add_node("planner", create_platoon_plan)
    workflow.add_node("router", lambda s: s)
    workflow.add_node("gestion_menu_lieutenant", lieutenant_node_placeholder)
    workflow.add_node("gestion_pedidos_lieutenant", lieutenant_node_placeholder)
    workflow.add_node("compiler", compile_final_report)

    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "router")
    workflow.add_conditional_edges("router", route_to_lieutenant, {
        "gestion_menu_lieutenant": "gestion_menu_lieutenant",
        "gestion_pedidos_lieutenant": "gestion_pedidos_lieutenant",
        "compile_report": "compiler",
        "router": "router"
    })
    workflow.add_edge("gestion_menu_lieutenant", "router")
    workflow.add_edge("gestion_pedidos_lieutenant", "router")
    workflow.add_edge("compiler", END)

    memory = SqliteSaver.from_conn_string(":memory:")
    return workflow.compile(checkpointer=memory)
