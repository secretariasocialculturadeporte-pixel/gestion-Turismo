import os
import logging
from huggingface_hub import hf_hub_download
from langchain_community.llms import LlamaCpp
from langchain.tools import tool
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, ToolMessage
from ..database import db_manager

# Configuración de LangSmith (Opcional)
os.environ["LANGCHAIN_TRACING_V2"] = "true"
langsmith_api_key = os.getenv("LANGSMITH_API_KEY")
if langsmith_api_key:
    os.environ["LANGCHAIN_API_KEY"] = langsmith_api_key
    os.environ["LANGCHAIN_PROJECT"] = "TurismoApp-Agente"

logger = logging.getLogger(__name__)

# --- Model Definition and Downloader ---
MODEL_REPO = "QuantFactory/Phi-3-mini-4k-instruct-GGUF"
MODEL_FILE = "Phi-3-mini-4k-instruct.Q2_K.gguf"
LOCAL_MODEL_DIR = "turismo_app/agents/local_agents"
MODEL_PATH = os.path.join(LOCAL_MODEL_DIR, MODEL_FILE)

def _download_model_if_not_exists():
    """Downloads the GGUF model from Hugging Face if it doesn't exist locally."""
    if not os.path.exists(MODEL_PATH):
        logger.info(f"El modelo no se encuentra en {MODEL_PATH}, iniciando descarga...")
        os.makedirs(LOCAL_MODEL_DIR, exist_ok=True)
        try:
            hf_hub_download(
                repo_id=MODEL_REPO,
                filename=MODEL_FILE,
                local_dir=LOCAL_MODEL_DIR,
                local_dir_use_symlinks=False,
                resume_download=True,
            )
            logger.info("Descarga del modelo completada.")
        except Exception as e:
            logger.error(f"Error al descargar el modelo: {e}", exc_info=True)
            raise
    else:
        logger.info(f"Modelo ya existe en {MODEL_PATH}.")

# Ensure the model is available when the module is loaded
_download_model_if_not_exists()
# --- End Model Definition and Downloader ---


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

# --- LLM Initialization ---
# Replaces the ChatOllama call with a local LlamaCpp instance.
llm = LlamaCpp(
    model_path=MODEL_PATH,
    n_gpu_layers=-1,  # Offload all layers to GPU if available
    n_batch=512,  # Should be between 1 and n_ctx, consider memory constraints
    n_ctx=4096,  # Context window size
    verbose=True, # Log progress
    temperature=0, # For deterministic tool use
    chat_format="llama-3" # Phi-3 uses a similar chat format
)
model_with_tools = llm.bind_tools(tools)
# --- End LLM Initialization ---

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
