import os
from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.utilities import SQLDatabase
from langchain_community.chat_models import ChatOllama
import logging

logger = logging.getLogger(__name__)

# --- Configuración del Agente ---
# NOTA IMPORTANTE: Requiere un servicio de Ollama corriendo con un modelo (ej. `ollama run llama3`)
db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'turismo_data_final.db')

def create_turismo_agent():
    """Crea y configura el agente SQL para interactuar con la base de datos de turismo."""
    logger.info(f"Conectando el agente a la base de datos en: {db_path}")
    try:
        db = SQLDatabase.from_uri(f"sqlite:///{db_path}")
        llm = ChatOllama(model="llama3", temperature=0)
        agent_executor = create_sql_agent(
            llm=llm,
            db=db,
            agent_type="openai-tools",
            verbose=True
        )
        return agent_executor
    except Exception as e:
        logger.error(f"Error al crear el agente SQL: {e}", exc_info=True)
        return None

def invoke_agent(agent, question):
    """Invoca al agente con una pregunta y obtiene la respuesta."""
    if agent is None:
        return "El agente de IA no está disponible. Verifique la conexión con el servicio de Ollama y la base de datos."
    try:
        response = agent.invoke({"input": question})
        return response.get("output", "No se pudo obtener una respuesta.")
    except Exception as e:
        logger.error(f"Error al invocar el agente: {e}", exc_info=True)
        return "Ocurrió un error al procesar tu pregunta. Asegúrate de que el servicio de Ollama esté corriendo."
