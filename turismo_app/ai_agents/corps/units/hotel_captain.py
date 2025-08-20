from typing import TypedDict, List
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from .platoons.gestion_hotel_teniente import get_gestion_hotel_lieutenant_graph

llm = ChatOpenAI(model="gpt-4o", temperature=0, model_kwargs={"response_format": {"type": "json_object"}})

class HotelTask(BaseModel):
    task_description: str = Field(description="La descripción detallada de la misión para el Teniente de Hotel.")
    responsible_lieutenant: str = Field(description="Debe ser 'GestionHotel'.")

class HotelPlan(BaseModel):
    plan: List[HotelTask]

class HotelCaptainState(TypedDict):
    coronel_order: str
    platoon_plan: HotelPlan | None
    task_queue: List[HotelTask]
    completed_missions: list
    final_report: str
    error: str | None

gestion_hotel_agent = get_gestion_hotel_lieutenant_graph()

async def create_platoon_plan(state: HotelCaptainState) -> HotelCaptainState:
    print("--- 🧠 CAP. HOTELES: Creando Plan de Pelotón... ---")
    plan = HotelPlan(plan=[
        HotelTask(task_description=state['coronel_order'], responsible_lieutenant='GestionHotel')
    ])
    state.update({"platoon_plan": plan, "task_queue": plan.plan.copy(), "completed_missions": []})
    return state

def route_to_lieutenant(state: HotelCaptainState):
    if not state["task_queue"]: return "compile_report"
    return "gestion_hotel_lieutenant"

async def lieutenant_node(state: HotelCaptainState) -> HotelCaptainState:
    mission = state["task_queue"].pop(0)
    print(f"--- 🔽 CAPITÁN (Hotel): Delegando a TTE. GESTION HOTEL -> '{mission.task_description}' ---")
    # result = await gestion_hotel_agent.ainvoke(...)
    state["completed_missions"].append({"lieutenant": "GestionHotel", "report": "Misión de hotel completada (simulado)."})
    return state

async def compile_final_report(state: HotelCaptainState) -> HotelCaptainState:
    report_body = "\n".join([f"- Reporte del Tte. de {m['lieutenant']}: {m['report']}" for m in state["completed_missions"]])
    state["final_report"] = f"Misión del área de Hoteles completada.\nResumen:\n{report_body}"
    return state

def get_hotel_captain_graph():
    workflow = StateGraph(HotelCaptainState)
    workflow.add_node("planner", create_platoon_plan)
    workflow.add_node("gestion_hotel_lieutenant", lieutenant_node)
    workflow.add_node("compiler", compile_final_report)

    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "gestion_hotel_lieutenant")
    workflow.add_edge("gestion_hotel_lieutenant", "compiler")
    workflow.add_edge("compiler", END)

    memory = SqliteSaver.from_conn_string(":memory:")
    return workflow.compile(checkpointer=memory)
