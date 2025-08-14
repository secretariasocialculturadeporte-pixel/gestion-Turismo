import time
import logging

logger = logging.getLogger(__name__)

# --- Implementación Simulada del Agente de IA ---

# NOTA IMPORTANTE:
# La implementación real del agente SQL (usando LangChain y Ollama)
# se colgaba en este entorno debido a un problema con la biblioteca `sqlite3`.
# Esta versión SIMULADA permite continuar con el desarrollo de la interfaz de usuario.
# Para usar el agente real, reemplace el contenido de este archivo con la
# implementación de LangChain cuando se ejecute en un entorno compatible.

class MockAgentExecutor:
    """Un agente simulado que devuelve respuestas predefinidas."""
    def invoke(self, input_data):
        question = input_data.get("input", "").lower()
        logger.info(f"[MOCK AGENT] Recibida la pregunta: {question}")
        time.sleep(1.5) # Simular tiempo de procesamiento

        # Lógica de respuesta simple y predefinida
        if "hola" in question:
            response = "¡Hola! Soy el Asistente de Turismo. ¿En qué puedo ayudarte hoy?"
        elif "empresas" in question or "hoteles" in question:
            response = "Actualmente hay 2 empresas registradas en el sistema: Hotel Jardín Mock y Restaurante El Poblado Mock."
        elif "atractivos" in question:
            response = "Por el momento no hay atractivos turísticos registrados en el sistema simulado."
        elif "gracias" in question:
            response = "¡De nada! Si tienes más preguntas, no dudes en consultarme."
        else:
            response = "No he podido procesar esa pregunta. Intenta preguntarme sobre empresas o atractivos turísticos."

        return {"output": response}

def create_turismo_agent():
    """Crea y retorna una instancia del agente SIMULADO."""
    logger.info("Creando el agente de turismo SIMULADO...")
    return MockAgentExecutor()

def invoke_agent(agent, question):
    """Función helper para invocar al agente simulado."""
    return agent.invoke({"input": question}).get("output")

# --- Ejemplo de uso ---
if __name__ == '__main__':
    print("Creando el agente de turismo SIMULADO...")
    turismo_agent = create_turismo_agent()

    print("\n--- Probando el agente simulado ---")
    question1 = "¿cuántas empresas hay?"
    answer1 = invoke_agent(turismo_agent, question1)
    print(f"\nPregunta: {question1}")
    print(f"Respuesta: {answer1}")

    question2 = "gracias"
    answer2 = invoke_agent(turismo_agent, question2)
    print(f"\nPregunta: {question2}")
    print(f"Respuesta: {answer2}")
