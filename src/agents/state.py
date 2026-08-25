from typing import Any, Literal, TypedDict
from langchain_core.messages import BaseMessage


class Chunk(TypedDict):
    id: str
    content: str
    metadata: dict[str, Any]


class ToolCall(TypedDict):
    id: str
    name: str
    arguments: dict[str, Any]


class ToolResult(TypedDict):
    tool_call_id: str
    tool_name: str
    content: str
    is_error: bool


class DefenseVerdict(TypedDict):
    source: Literal["retrieval", "tool_output"]
    content_hash: str
    heuristic_flagged: bool
    heuristic_reason: str | None
    judge_flagged: bool | None  # None if heuristic alone was decisive
    judge_reasoning: str | None
    action: Literal["pass", "sanitize", "block"]


class DefenseConfig(TypedDict):
    heuristic: bool
    llm_judge: bool
    classifier: bool


class AgentState(TypedDict):
    user_query: str
    messages: list[BaseMessage]

    raw_retrieved_chunks: list[Chunk]
    screened_chunks: list[Chunk]
    retrieval_flags: list[DefenseVerdict]

    tool_calls_requested: list[ToolCall]
    raw_tool_outputs: list[ToolResult]
    screened_tool_outputs: list[ToolResult]
    tool_flags: list[DefenseVerdict]

    next_agent: Literal["retriever", "tool_agent", "synthesizer", "end"]
    plan: str
    hop_count: int  # loop guard: incremented each retriever/tool_agent hop
    final_answer: str | None

    canary_leaked: bool
    unauthorized_tool_calls: list[ToolCall]
    defense_config: DefenseConfig
