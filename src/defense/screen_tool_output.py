from src.agents.state import AgentState, DefenseVerdict, ToolResult
from src.defense.heuristics import evaluate_heuristics
from src.defense.llm_judge import LLMJudge

_judge = None


def get_judge() -> LLMJudge:
    global _judge
    if _judge is None:
        _judge = LLMJudge()
    return _judge


def tool_output_screen_node(state: AgentState) -> dict:
    """Defense Hook B: Screens raw tool outputs before the orchestrator sees them.
    
    Protects against second-order / indirect prompt injections planted inside tools.
    """
    raw_outputs: list[ToolResult] = state.get("raw_tool_outputs", [])
    defense_cfg = state.get("defense_config", {"heuristic": False, "llm_judge": False, "classifier": False})

    screened_outputs: list[ToolResult] = []
    verdicts: list[DefenseVerdict] = []

    for tool_res in raw_outputs:
        text = tool_res["content"]
        verdict = evaluate_heuristics(text, source="tool_output")

        if not verdict["heuristic_flagged"] and defense_cfg.get("llm_judge", False):
            is_mal, reason = get_judge().judge_content(text, source="tool_output")
            verdict["judge_flagged"] = is_mal
            verdict["judge_reasoning"] = reason
            if is_mal:
                verdict["action"] = "block"

        verdicts.append(verdict)

        blocked = False
        if (verdict["heuristic_flagged"] and defense_cfg.get("heuristic", False)) or (verdict.get("judge_flagged") and defense_cfg.get("llm_judge", False)):
            blocked = True

        if blocked:
            screened_outputs.append({
                "tool_call_id": tool_res["tool_call_id"],
                "tool_name": tool_res["tool_name"],
                "content": "[BLOCKED BY DEFENSE LAYER: Potential prompt injection detected in tool result]",
                "is_error": True,
            })
        else:
            screened_outputs.append(tool_res)

    return {
        "screened_tool_outputs": screened_outputs,
        "tool_flags": state.get("tool_flags", []) + verdicts,
    }
