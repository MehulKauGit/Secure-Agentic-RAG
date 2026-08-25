from src.agents.graph import build_secure_rag_graph, graph_app
from src.agents.state import AgentState


def test_graph_compilation():
    graph = build_secure_rag_graph()
    app = graph.compile()
    assert app is not None


def test_graph_nodes():
    nodes = build_secure_rag_graph().nodes
    expected_nodes = {
        "orchestrator",
        "retriever",
        "retrieval_screen",
        "tool_agent",
        "tool_output_screen",
        "synthesizer",
    }
    assert expected_nodes.issubset(set(nodes.keys()))
