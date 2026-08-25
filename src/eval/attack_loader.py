import json
from pathlib import Path
from typing import Any

import jsonschema

CORPUS_ROOT = Path(__file__).resolve().parents[2] / "corpus"
SCHEMA_PATH = CORPUS_ROOT / "attack_schema.json"


def load_attack_schema() -> dict[str, Any]:
    with open(SCHEMA_PATH, encoding="utf-8") as f:
        return json.load(f)


def load_attacks_from_dir(directory: Path | str, validate: bool = True) -> list[dict[str, Any]]:
    """Loads and optionally validates all JSON attack files in a directory."""
    target_dir = Path(directory)
    if not target_dir.exists():
        return []

    schema = load_attack_schema() if validate else None
    attacks = []

    for file_path in target_dir.glob("*.json"):
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)
            items = data if isinstance(data, list) else [data]
            for item in items:
                if validate and schema:
                    jsonschema.validate(instance=item, schema=schema)
                attacks.append(item)

    return attacks


def load_dev_attacks(validate: bool = True) -> list[dict[str, Any]]:
    """Loads all attacks in the dev set (used for defense tuning)."""
    return load_attacks_from_dir(CORPUS_ROOT / "attacks" / "dev", validate=validate)


def load_held_out_attacks(validate: bool = True) -> list[dict[str, Any]]:
    """Loads all attacks in the held-out set (never used for tuning)."""
    return load_attacks_from_dir(CORPUS_ROOT / "attacks" / "held_out", validate=validate)


def load_mutations_attacks(validate: bool = True) -> list[dict[str, Any]]:
    """Loads all attack mutations."""
    return load_attacks_from_dir(CORPUS_ROOT / "attacks" / "mutations", validate=validate)
