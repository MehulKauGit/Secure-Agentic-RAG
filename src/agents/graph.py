from langgraph.graph import END, START, StateGraph
from src.agents.orchestrator import orchestrator_node
from src.agents.retriever import retriever_node
from src.agents.state import AgentState
from src.agents.synthesizer import synthesizer_node
from src.agents.tool_agent import tool_agent_node
from src.defense.screen_retrieval import retrieval_screen_node
from src.defense.screen_tool_output import tool_output_screen_node


MAX_HOPS = 5


def route_orchestrator(state: AgentState) -> str:
    """Conditional router based on orchestrator decision, with infinite-loop guard."""
    if state.get("hop_count", 0) >= MAX_HOPS:
        return "synthesizer"  # force termination
    next_action = state.get("next_agent", "synthesizer")
    if next_action == "retriever":
        return "retriever"
    elif next_action == "tool_agent":
        return "tool_agent"
    return "synthesizer"


def build_secure_rag_graph() -> StateGraph:
    """Constructs the LangGraph multi-agent workflow with loop-back defense screening."""
    workflow = StateGraph(AgentState)

    # Add core nodes
    workflow.add_node("orchestrator", orchestrator_node)
    workflow.add_node("retriever", retriever_node)
    workflow.add_node("retrieval_screen", retrieval_screen_node)
    workflow.add_node("tool_agent", tool_agent_node)
    workflow.add_node("tool_output_screen", tool_output_screen_node)
    workflow.add_node("synthesizer", synthesizer_node)

    # Start at orchestrator supervisor
    workflow.add_edge(START, "orchestrator")

    # Conditional routing from orchestrator
    workflow.add_conditional_edges(
        "orchestrator",
        route_orchestrator,
        {
            "retriever": "retriever",
            "tool_agent": "tool_agent",
            "synthesizer": "synthesizer",
        },
    )

    # Retrieval loop: retriever -> screening -> back to orchestrator
    workflow.add_edge("retriever", "retrieval_screen")
    workflow.add_edge("retrieval_screen", "orchestrator")

    # Tool loop: tool_agent -> screening -> back to orchestrator
    workflow.add_edge("tool_agent", "tool_output_screen")
    workflow.add_edge("tool_output_screen", "orchestrator")

    # Synthesizer is terminal node
    workflow.add_edge("synthesizer", END)

    return workflow


# Compiled default graph app instance
graph_app = build_secure_rag_graph().compile()
