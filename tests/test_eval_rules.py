from tuneforge.eval_rules import evaluate_response


def test_rules_can_pass():
    result = evaluate_response(
        "Neural networks learn patterns from data.",
        {
            "min_words": 4,
            "max_words": 10,
            "contains": ["patterns"],
            "not_contains": ["guaranteed"],
        },
    )

    assert result["passed"] is True


def test_rules_can_fail():
    result = evaluate_response(
        "Too short",
        {"min_words": 5},
    )

    assert result["passed"] is False
    assert result["passed_count"] == 0
