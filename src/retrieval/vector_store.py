from pathlib import Path
from typing import Any
import chromadb
from chromadb.config import Settings
from langchain_ollama import OllamaEmbeddings
from langchain_core.embeddings import Embeddings

CHROMA_PERSIST_DIR = Path(__file__).resolve().parents[2] / "data" / "chroma"
DEFAULT_COLLECTION_NAME = "secure_rag_docs"


class MockLocalEmbeddings(Embeddings):
    """Deterministic fallback embeddings when Ollama server is offline or loading."""

    def __init__(self, dim: int = 384):
        self.dim = dim

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(t) for t in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)

    def _embed(self, text: str) -> list[float]:
        # Generate pseudo-deterministic normalized vector from string hash
        import hashlib
        import math
        h = hashlib.sha256(text.encode()).digest()
        vec = [(b / 255.0) - 0.5 for b in h[: self.dim // 8]]
        # Repeat or pad to reach dim
        full_vec = (vec * (self.dim // len(vec) + 1))[: self.dim]
        norm = math.sqrt(sum(x * x for x in full_vec)) or 1.0
        return [x / norm for x in full_vec]


def get_embeddings(model_name: str = "nomic-embed-text", base_url: str = "http://localhost:11434") -> Embeddings:
    """Returns OllamaEmbeddings or falls back gracefully if unreachable."""
    try:
        return OllamaEmbeddings(model=model_name, base_url=base_url)
    except Exception:
        return MockLocalEmbeddings()


class VectorStore:
    def __init__(
        self,
        collection_name: str = DEFAULT_COLLECTION_NAME,
        persist_dir: Path | str = CHROMA_PERSIST_DIR,
        embedding_model: str = "nomic-embed-text",
    ):
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(
            path=str(self.persist_dir),
            settings=Settings(anonymized_telemetry=False),
        )
        self.collection_name = collection_name
        self.collection = self.client.get_or_create_collection(name=collection_name)
        self.embeddings = get_embeddings(model_name=embedding_model)

    def add_documents(
        self,
        docs: list[str],
        metadatas: list[dict[str, Any]],
        ids: list[str],
    ) -> None:
        """Adds text documents and their metadata to ChromaDB."""
        if not docs:
            return
        embeddings = self.embeddings.embed_documents(docs)
        self.collection.upsert(
            documents=docs,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids,
        )

    def query(self, query_text: str, top_k: int = 4) -> list[dict[str, Any]]:
        """Queries the vector store for top-k similar chunks."""
        query_embedding = self.embeddings.embed_query(query_text)
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
        )

        output_chunks = []
        if results and results["documents"]:
            docs = results["documents"][0]
            metas = results["metadatas"][0] if results["metadatas"] else [{}] * len(docs)
            ids = results["ids"][0] if results["ids"] else [""] * len(docs)
            distances = results["distances"][0] if "distances" in results and results["distances"] else [0.0] * len(docs)

            for doc_id, doc, meta, dist in zip(ids, docs, metas, distances):
                output_chunks.append({
                    "id": doc_id,
                    "content": doc,
                    "metadata": meta,
                    "distance": dist,
                })
        return output_chunks
