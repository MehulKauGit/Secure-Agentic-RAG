from datetime import datetime, timezone
import hashlib
from pathlib import Path
import subprocess
from typing import Any
import yaml

CONFIGS_DIR = Path(__file__).resolve().parents[2] / "configs" / "experiments"
DATA_RUNS_DIR = Path(__file__).resolve().parents[2] / "data" / "runs"


def get_git_commit_hash() -> str:
    try:
        res = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            check=False,
        )
        return res.stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def load_experiment_config(config_path_or_name: str) -> dict[str, Any]:
    """Loads an experiment YAML file either by direct path or config name (e.g. 'none', 'combined')."""
    p = Path(config_path_or_name)
    if not p.exists():
        # Look in configs/experiments/
        p = CONFIGS_DIR / f"{config_path_or_name}.yaml"
        if not p.exists():
            p = CONFIGS_DIR / config_path_or_name

    if not p.exists():
        raise FileNotFoundError(f"Experiment config not found: '{config_path_or_name}'")

    with open(p, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f) or {}

    config["git_commit"] = get_git_commit_hash()
    return config


def create_run_directory(config: dict[str, Any]) -> tuple[str, Path]:
    """Generates a unique run_id and creates data/runs/{run_id}/."""
    run_name = config.get("run_name", "experiment")
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    run_id = f"{run_name}_{ts}"

    run_dir = DATA_RUNS_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    # Save snapshot of config.yaml
    with open(run_dir / "config.yaml", "w", encoding="utf-8") as f:
        yaml.dump(config, f, default_flow_style=False)

    return run_id, run_dir
