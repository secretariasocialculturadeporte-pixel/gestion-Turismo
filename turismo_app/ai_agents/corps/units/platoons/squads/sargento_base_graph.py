from typing import TypedDict, Any, List, Annotated
import operator
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_openai import ChatOpenAI
from langchain_core.tools import BaseTool

class SargentoBaseState(TypedDict):
    """La pizarra táctica estandarizada para todos los Sargentos."""
    teniente_order: str
    app_context: Any # El historial de la misión, se va construyendo paso a paso
    messages: Annotated[List[BaseMessage], operator.add]
    final_report: str
    error: str | None

class SargentoGraphBuilder:
    """Constructor estandarizado para todos los agentes Sargento."""
    def __init__(self, squad: List[BaseTool], squad_name: str):
        self.squad_executor = ToolNode(squad)
        self.squad_name = squad_name
        # El cerebro es un LLM potente con capacidad de llamar a las herramientas (Soldados) de su escuadra
        self.model = ChatOpenAI(model="gpt-4o-2024-05-13", temperature=0).bind_tools(squad)

    def get_sargento_brain(self, state: SargentoBaseState):
        """El cerebro del Sargento. Analiza el estado y decide la siguiente acción para su escuadra."""
        print(f"--- 🤔 SARGENTO ({self.squad_name}): Analizando orden y decidiendo acción... ---")
        return self.model.invoke(state["messages"])

    def route_action(self, state: SargentoBaseState):
        """Revisa la decisión del cerebro y enruta al ejecutor o al informe final."""
        last_message = state["messages"][-1]
        # Si el LLM no devuelve una llamada a herramienta, la misión ha terminado
        if not hasattr(last_message, 'tool_calls') or not last_message.tool_calls:
            return "compile_report"
        return "squad_executor"

    def compile_report_node(self, state: SargentoBaseState) -> SargentoBaseState:
        """Compila el informe final para el Teniente a partir del historial de la misión."""
        print(f"--- 📄 SARGENTO ({self.squad_name}): Misión completada. Compilando reporte. ---")

        executed_steps = [f"Acción: {msg.name}, Resultado: {msg.content}" for msg in state["messages"] if msg.type == 'tool']

        if not executed_steps:
            report_body = "Misión completada sin necesidad de acciones directas de la escuadra."
        else:
            report_body = "\n- ".join(executed_steps)

        state["final_report"] = f"Misión completada. Resumen de acciones de la escuadra de {self.squad_name}:\n- {report_body}"
        return state

    def build_graph(self):
        """Construye y compila el grafo LangGraph para el Sargento."""
        workflow = StateGraph(SargentoBaseState)

        def mission_entry_node(state: SargentoBaseState):
            """Nodo de entrada que formatea la orden del Teniente como el primer mensaje."""
            return {"messages": [HumanMessage(content=state["teniente_order"])]}

        workflow.add_node("mission_entry", mission_entry_node)
        workflow.add_node("brain", self.get_sargento_brain)
        workflow.add_node("squad_executor", self.squad_executor)
        workflow.add_node("compiler", self.compile_report_node)

        workflow.add_edge(START, "mission_entry")
        workflow.add_edge("mission_entry", "brain")
        workflow.add_conditional_edges(
            "brain",
            self.route_action,
            {
                "squad_executor": "squad_executor",
                "compiler": "compiler"
            }
        )
        workflow.add_edge("squad_executor", "brain")
        workflow.add_edge("compiler", END)

        memory = SqliteSaver.from_conn_string(":memory:")
        return workflow.compile(checkpointer=memory)
