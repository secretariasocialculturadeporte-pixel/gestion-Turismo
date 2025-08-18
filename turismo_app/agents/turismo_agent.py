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

logger = logging.getLogger(__name__)

@tool
def buscar_hoteles(ciudad: str, num_personas: int):
    """Busca hoteles disponibles en una ciudad para un número de personas."""
    hoteles = db_manager.listar_recursos_por_tipo_y_ciudad("Habitacion", ciudad, num_personas)
    return f"Se encontraron {len(hoteles)} hoteles en {ciudad} para {num_personas} personas."

@tool
def buscar_guias(ciudad: str, especialidad: str):
    """Busca guías turísticos en una ciudad con una especialidad."""
    guias = db_manager.listar_guias_publico({"especialidad__icontains": especialidad, "ciudad": ciudad})
    return f"Se encontró {len(guias)} guía de {especialidad} en {ciudad}."

tools = [buscar_hoteles, buscar_guias]
tool_executor = lambda state: [ToolMessage(tool_call_id=tool_call.id, content=tool.invoke(tool_call.args)) for tool_call in state["messages"][-1].tool_calls]

llm = ChatOllama(model="llama3", temperature=0)
model_with_tools = llm.bind_tools(tools)

class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]

def should_continue(state):
    return "tool_calls" in state["messages"][-1].additional_kwargs

def call_model(state):
    response = model_with_tools.invoke(state["messages"])
    return {"messages": [response]}

workflow = StateGraph(AgentState)
workflow.add_node("agent", call_model)
workflow.add_node("action", tool_executor)
workflow.add_conditional_edge("agent", should_continue, {True: "action", False: END})
workflow.add_edge("action", "agent")
workflow.set_entry_point("agent")
app = workflow.compile()

def invoke_agent(question):
    try:
        response = app.invoke({"messages": [SystemMessage(content="Eres un asistente de planificación de viajes."), HumanMessage(content=question)]})
        return response["messages"][-1].content
    except Exception as e:
        logger.error(f"Error al invocar el agente: {e}", exc_info=True)
        return "Ocurrió un error al procesar tu pregunta."
