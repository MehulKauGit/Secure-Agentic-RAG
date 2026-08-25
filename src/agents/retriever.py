from typing import Any
from src.agents.state import AgentState, Chunk
from src.retrieval.vector_store import VectorStore

_store = None


def get_vector_store() -> VectorStore:
    global _store
    if _store is None:
        _store = VectorStore()
    return _store


def retriever_node(state: AgentState) -> dict[str, Any]:
    """Retrieval agent: queries ChromaDB for chunks matching user query."""
    user_query = state.get("user_query", "")
    store = get_vector_store()

    results = store.query(user_query, top_k=3)
    raw_chunks: list[Chunk] = [
        {
            "id": r["id"],
            "content": r["content"],
            "metadata": r.get("metadata", {}),
        }
        for r in results
    ]

    return {
        "raw_retrieved_chunks": raw_chunks,
        "hop_count": state.get("hop_count", 0) + 1,
    }
