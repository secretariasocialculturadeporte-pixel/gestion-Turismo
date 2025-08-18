import os
import logging
from langchain_community.chat_models import ChatOllama
from langchain.tools import tool
from langgraph.prebuilt import create_agent_executor
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, ToolMessage

# Configuración de LangSmith
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGSMITH_API_KEY")
os.environ["LANGCHAIN_PROJECT"] = "TurismoApp-Agente"

logger = logging.getLogger(__name__)

@tool
def buscar_recursos(tipo_recurso: str, ciudad: str, capacidad: int):
    """Busca recursos disponibles de un tipo específico en una ciudad para una capacidad determinada."""
    recursos = db_manager.listar_recursos_por_tipo_y_ciudad(tipo_recurso, ciudad, capacidad)
    return f"Se encontraron {len(recursos)} recursos de tipo '{tipo_recurso}' en {ciudad}."

@tool
def crear_reserva(id_recurso: int, id_cliente: int, fecha_inicio: str, fecha_fin: str):
    """Crea una reserva para un recurso específico."""
    # Lógica simplificada
    datos = {"id_recurso": id_recurso, "id_cliente": id_cliente, "fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin, "estado": "Confirmada"}
    reserva_id = db_manager.crear_o_actualizar_reserva(datos)
    return f"Reserva creada con ID: {reserva_id}"

@tool
def buscar_paquetes(destino: str, interes: str):
    """Busca paquetes turísticos en un destino según un interés."""
    paquetes = db_manager.listar_paquetes_por_agencia(1) # Placeholder para empresa 1
    return f"Se encontraron {len(paquetes)} paquetes en {destino}."

tools = [buscar_recursos, crear_reserva, buscar_paquetes]
tool_executor = lambda state: [ToolMessage(tool_call_id=tool_call.id, content=tool.invoke(tool_call.args)) for tool_call in state["messages"][-1].tool_calls]

llm = ChatOllama(model="llama3", temperature=0)
model_with_tools = llm.bind_tools(tools)

class PlanState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    plan: list[str]

def planner(state):
    # Lógica para analizar el estado y decidir el siguiente paso
    return {"messages": [SystemMessage(content="Planificador decidió buscar hoteles.")]}

def executor(state):
    # Lógica para ejecutar las herramientas
    return {"plan": ["Hotel ABC encontrado."]}

def updater(state):
    # Lógica para actualizar el plan
    return {"messages": [SystemMessage(content="Plan actualizado.")]}

workflow = StateGraph(PlanState)
workflow.add_node("planner", planner)
workflow.add_node("executor", executor)
workflow.add_node("updater", updater)
workflow.set_entry_point("planner")
workflow.add_edge("planner", "executor")
workflow.add_edge("executor", "updater")
workflow.add_edge("updater", END)
app = workflow.compile()

def invoke_agent(question):
    try:
        response = app.invoke({"messages": [HumanMessage(content=question)]})
        return response["messages"][-1].content
    except Exception as e:
        logger.error(f"Error al invocar el agente: {e}", exc_info=True)
        return "Ocurrió un error al procesar tu pregunta."
