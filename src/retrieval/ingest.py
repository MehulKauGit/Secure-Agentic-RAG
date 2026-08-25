import hashlib
from pathlib import Path

from src.retrieval.vector_store import VectorStore

DOCS_DIR = Path(__file__).resolve().parents[2] / "corpus" / "documents"


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """Simple sliding window chunker."""
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i : i + chunk_size])
        if chunk:
            chunks.append(chunk)
        i += chunk_size - overlap
    return chunks or [text]


def ingest_documents(docs_dir: Path = DOCS_DIR, vector_store: VectorStore | None = None) -> int:
    """Loads all documents from corpus/documents/ into ChromaDB."""
    if vector_store is None:
        vector_store = VectorStore()

    doc_files = list(docs_dir.glob("*.md")) + list(docs_dir.glob("*.txt"))
    all_chunks = []
    all_metadatas = []
    all_ids = []

    for file_path in doc_files:
        content = file_path.read_text(encoding="utf-8")
        chunks = chunk_text(content)
        for idx, chunk in enumerate(chunks):
            chunk_id = hashlib.sha256(f"{file_path.name}_{idx}_{chunk[:30]}".encode()).hexdigest()[:16]
            all_chunks.append(chunk)
            all_metadatas.append({
                "source_file": file_path.name,
                "chunk_index": idx,
                "is_attack": False,
                "attack_id": None,
            })
            all_ids.append(chunk_id)

    if all_chunks:
        vector_store.add_documents(
            docs=all_chunks,
            metadatas=all_metadatas,
            ids=all_ids,
        )
    return len(all_chunks)


def ingest_attack_chunks(
    attacks: list[dict],
    vector_store: VectorStore | None = None,
) -> int:
    """Interleaves attack payloads into ChromaDB for retrieval-based attack evaluations."""
    if vector_store is None:
        vector_store = VectorStore()

    all_chunks = []
    all_metadatas = []
    all_ids = []

    for attack in attacks:
        payload = attack["payload"]
        aid = attack["attack_id"]
        cid = hashlib.sha256(f"attack_{aid}_{payload[:30]}".encode()).hexdigest()[:16]

        all_chunks.append(payload)
        all_metadatas.append({
            "source_file": "adversarial_corpus",
            "chunk_index": 0,
            "is_attack": True,
            "attack_id": aid,
            "attack_category": attack.get("attack_category", "unknown"),
        })
        all_ids.append(cid)

    if all_chunks:
        vector_store.add_documents(
            docs=all_chunks,
            metadatas=all_metadatas,
            ids=all_ids,
        )
    return len(all_chunks)


if __name__ == "__main__":
    count = ingest_documents()
    print(f"Successfully ingested {count} clean chunks into ChromaDB.")
