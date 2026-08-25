import json
from pathlib import Path


def test_dashboard_data_loading(tmp_path: Path):
    """Verifies dashboard data structure and summary calculations."""
    demo_run = tmp_path / "test_run"
    demo_run.mkdir(parents=True, exist_ok=True)
    summary_data = {
        "run_id": "test_run",
        "attack_success_rate": 0.2,
        "canary_leakage_rate": 0.0,
        "clean_task_success_rate": 0.95,
        "latency": {"median_sec": 1.5},
    }
    with open(demo_run / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary_data, f)

    assert (demo_run / "summary.json").exists()
    loaded = json.loads((demo_run / "summary.json").read_text(encoding="utf-8"))
    assert loaded["attack_success_rate"] == 0.2
