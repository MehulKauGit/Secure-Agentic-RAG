import argparse
import sys
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from src.agents.graph import graph_app
from src.agents.state import AgentState
from src.retrieval.ingest import ingest_documents

console = Console()


def run_pipeline(
    query: str,
    enable_heuristic: bool = False,
    enable_llm_judge: bool = False,
) -> dict:
    """Executes a single query through the Secure Agentic RAG graph."""
    initial_state: AgentState = {
        "user_query": query,
        "messages": [],
        "raw_retrieved_chunks": [],
        "screened_chunks": [],
        "retrieval_flags": [],
        "tool_calls_requested": [],
        "raw_tool_outputs": [],
        "screened_tool_outputs": [],
        "tool_flags": [],
        "next_agent": "retriever",
        "plan": "Initial orchestrator start",
        "final_answer": None,
        "canary_leaked": False,
        "unauthorized_tool_calls": [],
        "defense_config": {
            "heuristic": enable_heuristic,
            "llm_judge": enable_llm_judge,
            "classifier": False,
        },
    }

    final_state = graph_app.invoke(initial_state)
    return final_state


def main():
    parser = argparse.ArgumentParser(description="Secure Agentic RAG CLI")
    parser.add_argument("--query", "-q", type=str, help="User query to run")
    parser.add_argument("--heuristic", action="store_true", help="Enable heuristic defense screening")
    parser.add_argument("--judge", action="store_true", help="Enable LLM judge defense screening")
    parser.add_argument("--ingest", action="store_true", help="Ingest documents into ChromaDB first")
    args = parser.parse_args()

    if args.ingest:
        console.print("[bold blue]Ingesting documents into ChromaDB...[/bold blue]")
        count = ingest_documents()
        console.print(f"[bold green]✓ Ingested {count} chunks into ChromaDB.[/bold green]")

    if not args.query:
        console.print("[yellow]No query provided. Run with --query 'your question' or --ingest to index docs.[/yellow]")
        return

    console.print(Panel(f"[bold white]{args.query}[/bold white]", title="[bold cyan]User Query[/bold cyan]"))
    console.print(f"[dim]Defenses: Heuristics={'ON' if args.heuristic else 'OFF'}, LLM Judge={'ON' if args.judge else 'OFF'}[/dim]")

    result = run_pipeline(
        query=args.query,
        enable_heuristic=args.heuristic,
        enable_llm_judge=args.judge,
    )

    console.print("\n[bold green]Final Answer:[/bold green]")
    console.print(result.get("final_answer", "No answer produced."))

    # Display flags if any
    flags = result.get("retrieval_flags", []) + result.get("tool_flags", [])
    if flags:
        table = Table(title="🛡️ Defense Screening Verdicts")
        table.add_column("Source", style="cyan")
        table.add_column("Heuristic Flag", style="magenta")
        table.add_column("Judge Flag", style="yellow")
        table.add_column("Action", style="red")
        table.add_column("Reason")
        for f in flags:
            reason = f.get("heuristic_reason") or f.get("judge_reasoning") or "Clean"
            table.add_row(
                f.get("source", ""),
                str(f.get("heuristic_flagged", False)),
                str(f.get("judge_flagged", "")),
                f.get("action", ""),
                reason,
            )
        console.print(table)


if __name__ == "__main__":
    main()
