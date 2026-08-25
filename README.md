# Secure Agentic RAG Platform

> A production-style agentic RAG assistant with a built-in adversary. Multi-agent orchestration (LangGraph) exposes tools via MCP, a toggleable defense layer screens retrieved content and tool outputs for prompt injection, and an evaluation harness + dashboard prove — with numbers — that the defense reduces attack success without wrecking task utility. **Fully local: Ollama + Chroma, zero API spend.**

See [`secure_agentic_rag_architecture.md`](./secure_agentic_rag_architecture.md) for the full architecture & implementation guide.

---

## Prerequisites

You need three things on any machine before you start:

| Tool | Install |
|---|---|
| **Git** | [git-scm.com](https://git-scm.com/downloads) |
| **uv** (Python package manager) | `winget install astral-sh.uv` or see [docs.astral.sh/uv](https://docs.astral.sh/uv/getting-started/installation/) |
| **Ollama** (local LLM runtime) | [ollama.com/download](https://ollama.com/download) — run the installer, then `ollama serve` |

> **No Python installation needed.** `uv` manages Python automatically based on `.python-version`.

---

## Quick Start (any PC, from scratch)

```powershell
# 1. Clone
git clone https://github.com/<your-handle>/Secure-agentic-RAG-app.git
cd Secure-agentic-RAG-app

# 2. Install Python + all dependencies (one command)
uv sync

# 3. Pull the required Ollama models
ollama pull qwen2.5:7b-instruct-q4_K_M   # primary LLM
ollama pull nomic-embed-text              # embeddings
# Optional fallback (low-VRAM machines)
# ollama pull llama3.2:3b

# 4. Activate the virtual environment (PowerShell)
.\.venv\Scripts\Activate.ps1

# 5. Verify everything works
uv run python -c "import langgraph, chromadb, mcp; print('All good!')"
```

> If `ollama serve` isn't running as a background service, open a separate terminal and run it before step 5.

---

## Development Commands

```powershell
# Run tests
uv run pytest

# Lint
uv run ruff check src/

# Type-check
uv run mypy src/
```

---

## Project Structure

See the architecture doc for a full breakdown. Top-level layout:

```
├── configs/        # model + defense + experiment configs (YAML)
├── corpus/         # clean documents + attack corpus (dev / held-out / mutations)
├── src/
│   ├── agents/     # LangGraph graph, state schema, agent nodes
│   ├── defense/    # heuristic screen + LLM judge
│   ├── mcp_server/ # MCP tool server (calculator, file_lookup, send_email canary)
│   ├── retrieval/  # ChromaDB wrapper + ingestion
│   ├── eval/       # evaluation harness + metrics
│   └── dashboard/  # Streamlit dashboard
├── data/           # generated at runtime — NOT committed to git
│   ├── chroma/     # vector store persistence
│   └── runs/       # trajectory logs + summary.json per eval run
└── tests/
```

---

## Implementation Status

- [ ] **Phase 1** — Core pipeline (LangGraph wiring, Ollama, Chroma, MCP server, end-to-end query)
- [ ] **Phase 2** — Attack corpus + defense layer (heuristics + LLM judge)
- [ ] **Phase 3** — Held-out set, mutations, eval harness
- [ ] **Phase 4** — Streamlit dashboard + README polish
