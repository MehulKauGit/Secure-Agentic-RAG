import hashlib
import re
from pathlib import Path
from typing import Any
import yaml
from src.agents.state import DefenseVerdict

CONFIG_PATH = Path(__file__).resolve().parents[2] / "configs" / "defense.yaml"


def load_defense_config() -> dict[str, Any]:
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}


_config = load_defense_config()
_patterns: list[dict[str, Any]] = _config.get("heuristics", {}).get("regex_patterns", [])
_compiled_patterns = [
    (p.get("name", "unnamed"), re.compile(p["pattern"]), p.get("severity", "medium"))
    for p in _patterns
    if "pattern" in p
]


def evaluate_heuristics(content: str, source: str = "retrieval") -> DefenseVerdict:
    """Runs regex and rule heuristics on the given text content."""
    content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]
    
    if not content:
        return {
            "source": source,  # type: ignore
            "content_hash": content_hash,
            "heuristic_flagged": False,
            "heuristic_reason": None,
            "judge_flagged": None,
            "judge_reasoning": None,
            "action": "pass",
        }

    for name, pattern, severity in _compiled_patterns:
        if pattern.search(content):
            return {
                "source": source,  # type: ignore
                "content_hash": content_hash,
                "heuristic_flagged": True,
                "heuristic_reason": f"Matched heuristic rule [{name}] ({severity} severity)",
                "judge_flagged": None,
                "judge_reasoning": None,
                "action": "block" if severity in ("high", "critical") else "sanitize",
            }

    return {
        "source": source,  # type: ignore
        "content_hash": content_hash,
        "heuristic_flagged": False,
        "heuristic_reason": None,
        "judge_flagged": None,
        "judge_reasoning": None,
        "action": "pass",
    }
