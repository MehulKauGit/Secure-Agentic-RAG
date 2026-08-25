# 🛡️ Secure Agentic RAG Platform

> A production-style agentic RAG assistant with a built-in adversary. Multi-agent orchestration (**LangGraph**) exposes tools via **MCP**, a toggleable defense layer screens retrieved content and tool outputs for prompt injection, and an evaluation harness + dashboard prove — with numbers, not vibes — that the defense reduces attack success without degrading task utility. **Fully local: Ollama + Chroma, zero API spend.**

---

## 🏛️ System Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│              USER (CLI / minimal chat interface)                 │
└────────────────────────────────┬─────────────────────────────────┘
                                  │ query
                     ┌────────────▼────────────┐
                     │      Orchestrator        │
                     │  (LangGraph supervisor)  │
                     └───┬──────────────────┬───┘
                         │ delegates         │ delegates
              ┌──────────▼────────┐  ┌───────▼─────────────┐
              │  Retriever agent   │  │  Tool-use agent      │
              └──────────┬─────────┘  └───────┬───────────────┘
                         │                    │
              ┌──────────▼────────┐  ┌────────▼──────────────┐
              │  Chroma vector DB │  │   MCP tool server       │
              │  (document corpus,│  │  calculator · file      │
              │  attack-laced +   │  │  lookup · send_email    │
              │  clean chunks)    │  │  (canary, logged-only)  │
              └──────────┬────────┘  └────────┬──────────────┘
                         │                    │
                         ▼                    ▼
              ┌────────────────────────────────────────────┐
              │          Defense screening layer             │
              │  heuristics + LLM judge, per-hook toggle     │
              │  emits a DefenseVerdict per chunk/tool-result│
              └───────────────────┬────────────────────────┘
                                  │ back to orchestrator (loop)
                                  ▼
                       ┌─────────────────────┐
                       │  Synthesizer agent   │
                       └──────────┬───────────┘
                                  │ final answer
                                  ▼
                       ┌─────────────────────┐
                       │  Trajectory logger   │──► data/runs/{run_id}/
                       └─────────────────────┘

     ┌─────────────────────────────────────────────────────┐
     │   Evaluation harness (offline, batch)                 │
     │   replays dev + held-out + mutation attack sets,       │
     │   and clean tasks, across N defense configs             │
     └───────────────────────────┬───────────────────────────┘
                                 │ summary.json per run
                                 ▼
                     ┌───────────────────────┐
                     │   Streamlit dashboard   │
                     │  ASR / utility / Δ /    │
                     │  latency, before-after   │
                     └───────────────────────┘
```

---

## ⚡ Quick Start (Any PC, from scratch)

### Prerequisites

| Tool | Installation |
|---|---|
| **Git** | [git-scm.com](https://git-scm.com/downloads) |
| **uv** | `winget install astral-sh.uv` or see [docs.astral.sh/uv](https://docs.astral.sh/uv/) |
| **Ollama** | [ollama.com/download](https://ollama.com/download) |

> **No manual Python install needed!** `uv` manages Python automatically based on `.python-version`.

### Setup & Run in 4 Commands

```powershell
# 1. Clone the repository
git clone https://github.com/MehulKauGit/Secure-Agentic-RAG.git
cd Secure-Agentic-RAG

# 2. Sync all dependencies into isolated virtualenv (one command)
uv sync

# 3. Pull the local models (in separate terminal with ollama serve running)
ollama pull qwen2.5:7b-instruct-q4_K_M
ollama pull nomic-embed-text

# 4. Run the automated test suite
uv run pytest
```

---

## 🔬 Running the Platform

### 1. Interactive CLI & Real-time Query
```powershell
# Ingest clean knowledge base into ChromaDB
uv run python -m src.main --ingest

# Run an inquiry with active defense screening
uv run python -m src.main --query "What is the per diem meal allowance in Austin?" --heuristic --judge
```

### 2. Batch Evaluation Harness (ASR & Utility Benchmark)
```powershell
# Evaluate baseline (no defense)
uv run python -m src.eval.runner --config none --split all

# Evaluate combined defense (heuristics + LLM judge)
uv run python -m src.eval.runner --config combined --split all
```
*Evaluations output snapshot configs, raw `trajectories.jsonl`, and aggregate `summary.json` inside `data/runs/{run_id}/`.*

### 3. Interactive Streamlit Dashboard
```powershell
uv run streamlit run src/dashboard/app.py
```
Open [http://localhost:8501](http://localhost:8501) to compare benchmark runs side-by-side, inspect trajectories, and test live adversarial payloads in the playground.

---

## 📁 Project Structure

```
Secure-Agentic-RAG/
├── configs/
│   ├── models.yaml                    # Model + embedding configuration
│   ├── defense.yaml                   # Heuristic rule bank + LLM judge template
│   └── experiments/                   # Experiment presets (none, heuristic, judge, combined)
├── corpus/
│   ├── documents/                     # Clean knowledge base documents
│   ├── attacks/                       # Adversarial corpus
│   │   ├── dev/                       # 24 attacks for defense tuning
│   │   ├── held_out/                  # 11 held-out attacks for generalization testing
│   │   └── mutations/                 # Evasion variants (casing, leetspeak, spacing, preambles)
│   └── attack_schema.json             # JSON schema validation for all attacks
├── src/
│   ├── agents/                        # LangGraph StateGraph, supervisor, retriever, tool, synthesizer
│   ├── defense/                       # Heuristic regex screening & LLM judge nodes
│   ├── mcp_server/                    # FastMCP tool server (calculator, file_lookup, send_email canary)
│   ├── retrieval/                     # ChromaDB vector store wrapper & ingestion
│   ├── eval/                          # Eval runner, success criteria, metrics, mutations
│   └── dashboard/                     # Streamlit comparison dashboard
├── data/                              # Runtime databases & run artifacts (gitignored)
└── tests/                             # 19 comprehensive pytest unit & integration tests
```

---

## 🛡️ Key Defenses & Architectural Highlights

- **Real Model Context Protocol (MCP)**: Implements standard FastMCP tools with canary secret exfiltration detection.
- **LangGraph Supervisor with Loop-Back Edges**: Content retrieved from Chroma or returned by tools is routed through defense nodes before the supervisor or synthesizer ever inspects it.
- **Objective Ground-Truth Evaluation**: ASR is evaluated against explicit ground-truth conditions (`canary_string_present_in_final_answer`, `unauthorized_send_email_call`, `contains_phrase:<phrase>`) rather than subjective LLM self-reporting.
- **Full Traceability**: Every evaluation run captures exact git commit hashes, full trajectory logs, and counterfactual verdicts.
