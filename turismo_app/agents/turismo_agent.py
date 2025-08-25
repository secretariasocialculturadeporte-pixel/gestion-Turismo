import os
import logging
from typing import TypedDict, Annotated
import operator

from huggingface_hub import hf_hub_download
from langchain_community.llms import LlamaCpp
from langchain_community.chat_models import ChatOllama # Keep for original reference if needed
from langchain.tools import tool
from langgraph.graph import StateGraph, END
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, ToolMessage
from langgraph.prebuilt import chat_agent_executor

# It's better to handle the db_manager import within the tools, but for now, let's keep it here.
from ..database import db_manager

# --- Basic Configuration ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Optional LangSmith Configuration ---
os.environ["LANGCHAIN_TRACING_V2"] = "true"
langsmith_api_key = os.getenv("LANGSMITH_API_KEY")
if langsmith_api_key:
    os.environ["LANGCHAIN_API_KEY"] = langsmith_api_key
    os.environ["LANGCHAIN_PROJECT"] = "TurismoApp-Agente-Dinamico"

# --- Hardware Detection ---
def get_device_ram_gb():
    """
    Detects the total RAM of the device in gigabytes.
    Reads /proc/meminfo on Linux/Android systems.
    Returns a default of 16GB for other platforms (e.g., Windows) or if reading fails.
    """
    try:
        with open('/proc/meminfo', 'r') as mem:
            for line in mem:
                if 'MemTotal' in line:
                    total_kb = int(line.split()[1])
                    total_gb = total_kb / (1024 * 1024)
                    logger.info(f"Detected device RAM: {total_gb:.2f} GB")
                    return total_gb
    except FileNotFoundError:
        logger.warning("/proc/meminfo not found. Defaulting to 16GB RAM (assuming PC environment).")
        return 16.0
    except Exception as e:
        logger.error(f"Could not determine device RAM. Defaulting to 16GB. Error: {e}")
        return 16.0

# --- Model & Tier Definitions ---
LOCAL_MODEL_DIR = "turismo_app/agents/local_agents"
MODEL_TIERS = {
    "HIGH": {
        "ram_threshold_gb": 7.0,
        "repo_id": "QuantFactory/Phi-3-mini-4k-instruct-GGUF",
        "filename": "Phi-3-mini-4k-instruct.Q2_K.gguf",
        "chat_format": "llama-3",
    },
    "MID": {
        "ram_threshold_gb": 3.5,
        "repo_id": "mlabonne/gemma-2b-it-GGUF",
        "filename": "gemma-2b-it.Q2_K.gguf",
        "chat_format": "gemma",
    },
    "LOW": {
        "ram_threshold_gb": 0,
        "engine": "RULE_BASED"
    }
}

def _download_model(tier_config):
    """Downloads a model file based on the selected tier's configuration."""
    model_path = os.path.join(LOCAL_MODEL_DIR, tier_config["filename"])
    if not os.path.exists(model_path):
        logger.info(f"Model for tier not found. Downloading '{tier_config['filename']}'...")
        os.makedirs(LOCAL_MODEL_DIR, exist_ok=True)
        try:
            hf_hub_download(
                repo_id=tier_config["repo_id"],
                filename=tier_config["filename"],
                local_dir=LOCAL_MODEL_DIR,
                local_dir_use_symlinks=False,
            )
            logger.info("Download complete.")
        except Exception as e:
            logger.error(f"Error downloading model: {e}", exc_info=True)
            raise
    else:
        logger.info(f"Model '{tier_config['filename']}' already exists.")
    return model_path

def initialize_agent_engine():
    """
    Detects hardware, selects the appropriate tier, downloads the model if needed,
    and returns the configured agent engine (LLM instance or rule-based identifier).
    """
    ram_gb = get_device_ram_gb()

    selected_tier_name = "LOW" # Default to low tier
    if ram_gb > MODEL_TIERS["HIGH"]["ram_threshold_gb"]:
        selected_tier_name = "HIGH"
    elif ram_gb > MODEL_TIERS["MID"]["ram_threshold_gb"]:
        selected_tier_name = "MID"

    logger.info(f"Device RAM is {ram_gb:.2f}GB. Selected Tier: {selected_tier_name}")

    tier_config = MODEL_TIERS[selected_tier_name]

    if "engine" in tier_config and tier_config["engine"] == "RULE_BASED":
        return "RULE_BASED"

    try:
        model_path = _download_model(tier_config)
        llm = LlamaCpp(
            model_path=model_path,
            n_gpu_layers=-1,
            n_batch=512,
            n_ctx=4096,
            verbose=False,
            temperature=0,
            chat_format=tier_config["chat_format"]
        )
        return llm
    except Exception as e:
        logger.error(f"Failed to initialize LlamaCpp. Falling back to RULE_BASED. Error: {e}")
        return "RULE_BASED"

# --- Agent Tools ---
@tool
def buscar_recursos(tipo_recurso: str, ciudad: str, capacidad: int):
    """Busca recursos disponibles de un tipo específico en una ciudad para una capacidad determinada."""
    # This is a placeholder. In a real app, you'd query a database.
    logger.info(f"TOOL CALLED: buscar_recursos(tipo_recurso='{tipo_recurso}', ciudad='{ciudad}', capacidad={capacidad})")
    return f"Se encontraron 5 recursos de tipo '{tipo_recurso}' en {ciudad}."

@tool
def crear_reserva(id_recurso: int, id_cliente: int, fecha_inicio: str, fecha_fin: str):
    """Crea una reserva para un recurso específico."""
    logger.info(f"TOOL CALLED: crear_reserva(...)")
    return f"Reserva creada con ID: 800."

@tool
def buscar_paquetes(destino: str, interes: str):
    """Busca paquetes turísticos en un destino según un interés."""
    logger.info(f"TOOL CALLED: buscar_paquetes(destino='{destino}', interes='{interes}')")
    return f"Se encontraron 3 paquetes en {destino}."

# --- Rule-Based System ---
def run_rule_based_system(question: str):
    """
    A simple keyword-based routing system for low-end devices.
    It bypasses the LLM and calls tools directly based on keywords.
    """
    logger.info("Executing with Rule-Based System.")
    q_lower = question.lower()

    # Very basic argument extraction - assumes format like "in <city>"
    def extract_arg(text, keyword):
        try:
            return text.split(keyword)[1].strip().split()[0]
        except IndexError:
            return None

    if "buscar recursos" in q_lower or ("buscar" in q_lower and "hotel" in q_lower):
        ciudad = extract_arg(q_lower, "en ") or "any"
        # Assume default capacity for simplicity
        capacidad = 2
        return buscar_recursos.invoke({"tipo_recurso": "hotel", "ciudad": ciudad, "capacidad": capacidad})

    if "crear reserva" in q_lower:
        # Cannot extract args reliably, return a message to guide the user
        return "Para crear una reserva, por favor especifica los detalles exactos."

    if "buscar paquetes" in q_lower:
        destino = extract_arg(q_lower, "en ") or "any"
        interes = extract_arg(q_lower, "de ") or "any"
        return buscar_paquetes.invoke({"destino": destino, "interes": interes})

    return "No pude entender tu solicitud. Por favor, intenta usar frases como 'buscar hoteles en Bogotá' o 'buscar paquetes de aventura'."


# --- Main Agent Logic ---
tools = [buscar_recursos, crear_reserva, buscar_paquetes]
# Initialize engine on first use, not on module load.
agent_engine = None

def get_agent_engine():
    """Initializes the agent engine on first call and caches it."""
    global agent_engine
    if agent_engine is None:
        agent_engine = initialize_agent_engine()
    return agent_engine

def invoke_agent(question):
    """
    Invokes the appropriate agent logic based on the initialized engine.
    """
    engine = get_agent_engine()
    if engine != "RULE_BASED":
        logger.info("Invoking agent with LLM Engine.")
        try:
            # Create a proper tool-calling agent executor
            graph = chat_agent_executor.create(engine, tools)
            response = graph.invoke({"messages": [HumanMessage(content=question)]})
            # The final response is in the 'messages' list
            return response["messages"][-1].content
        except Exception as e:
            logger.error(f"Error invoking LLM agent: {e}", exc_info=True)
            return "Ocurrió un error al procesar tu pregunta con el LLM."
    elif engine == "RULE_BASED":
        logger.info("Invoking agent with Rule-Based Engine.")
        return run_rule_based_system(question)

# The rest of the file contains the original LangGraph placeholder, which is not currently used
# by the simplified invoke_agent but is preserved.
class PlanState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    plan: list[str]

def planner(state):
    return {"messages": [SystemMessage(content="Planificador decidió buscar hoteles.")]}

def executor(state):
    return {"plan": ["Hotel ABC encontrado."]}

def updater(state):
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
