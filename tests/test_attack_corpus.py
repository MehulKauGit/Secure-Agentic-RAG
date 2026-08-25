from src.defense.heuristics import evaluate_heuristics
from src.eval.attack_loader import load_dev_attacks


def test_dev_attacks_loaded_and_valid():
    """Ensures all dev attack JSON files conform strictly to attack_schema.json."""
    attacks = load_dev_attacks(validate=True)
    assert len(attacks) >= 20, f"Expected at least 20 dev attacks, found {len(attacks)}"

    categories = {a["attack_category"] for a in attacks}
    expected_categories = {
        "direct_override",
        "second_order_injection",
        "exfiltration",
        "tool_misuse_coercion",
    }
    assert expected_categories.issubset(categories)


def test_heuristic_screens_dev_attacks():
    """Tests that heuristic rules flag known direct overrides and exfiltration attacks."""
    attacks = load_dev_attacks(validate=True)
    flagged_count = 0

    for a in attacks:
        verdict = evaluate_heuristics(a["payload"], source="retrieval")
        if verdict["heuristic_flagged"]:
            flagged_count += 1

    # Heuristics should catch a large portion of dev attacks without needing LLM judge
    assert flagged_count >= 15, f"Expected heuristics to catch at least 15 dev attacks, caught {flagged_count}"
