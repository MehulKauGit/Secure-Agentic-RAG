from src.agents.state import AgentState, Chunk, DefenseVerdict
from src.defense.heuristics import evaluate_heuristics
from src.defense.llm_judge import LLMJudge

_judge = None


def get_judge() -> LLMJudge:
    global _judge
    if _judge is None:
        _judge = LLMJudge()
    return _judge


def retrieval_screen_node(state: AgentState) -> dict:
    """Defense Hook A: Screens raw retrieved chunks before the orchestrator sees them.
    
    If defense is disabled in defense_config, it still evaluates and logs DefenseVerdicts
    (for audit/counterfactual tracking), but does not block the chunk.
    """
    raw_chunks: list[Chunk] = state.get("raw_retrieved_chunks", [])
    defense_cfg = state.get("defense_config", {"heuristic": False, "llm_judge": False, "classifier": False})

    screened_chunks: list[Chunk] = []
    verdicts: list[DefenseVerdict] = []

    for chunk in raw_chunks:
        text = chunk["content"]
        verdict = evaluate_heuristics(text, source="retrieval")

        # Second pass: LLM judge if heuristics didn't flag and judge defense is enabled
        if not verdict["heuristic_flagged"] and defense_cfg.get("llm_judge", False):
            is_mal, reason = get_judge().judge_content(text, source="retrieval")
            verdict["judge_flagged"] = is_mal
            verdict["judge_reasoning"] = reason
            if is_mal:
                verdict["action"] = "block"

        verdicts.append(verdict)

        # Check if we should enforce blocking
        blocked = False
        if verdict["heuristic_flagged"] and defense_cfg.get("heuristic", False):
            blocked = True
        elif verdict.get("judge_flagged") and defense_cfg.get("llm_judge", False):
            blocked = True

        if not blocked:
            screened_chunks.append(chunk)

    return {
        "screened_chunks": screened_chunks,
        "retrieval_flags": state.get("retrieval_flags", []) + verdicts,
    }
