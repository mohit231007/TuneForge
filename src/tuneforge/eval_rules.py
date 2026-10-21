from __future__ import annotations

import re
from typing import Any


def evaluate_response(response: str, rules: dict[str, Any] | None = None) -> dict[str, Any]:
    rules = rules or {}
    checks: list[dict[str, Any]] = []
    words = response.split()

    if "min_words" in rules:
        target = int(rules["min_words"])
        checks.append({
            "name": "min_words",
            "passed": len(words) >= target,
            "observed": len(words),
            "expected": target,
        })

    if "max_words" in rules:
        target = int(rules["max_words"])
        checks.append({
            "name": "max_words",
            "passed": len(words) <= target,
            "observed": len(words),
            "expected": target,
        })

    for needle in rules.get("contains", []):
        checks.append({
            "name": f"contains:{needle}",
            "passed": needle.lower() in response.lower(),
            "observed": needle.lower() in response.lower(),
            "expected": True,
        })

    for needle in rules.get("not_contains", []):
        checks.append({
            "name": f"not_contains:{needle}",
            "passed": needle.lower() not in response.lower(),
            "observed": needle.lower() not in response.lower(),
            "expected": True,
        })

    for pattern in rules.get("regex", []):
        matched = re.search(pattern, response) is not None
        checks.append({
            "name": f"regex:{pattern}",
            "passed": matched,
            "observed": matched,
            "expected": True,
        })

    passed = all(check["passed"] for check in checks) if checks else True

    return {
        "passed": passed,
        "check_count": len(checks),
        "passed_count": sum(1 for check in checks if check["passed"]),
        "checks": checks,
    }
