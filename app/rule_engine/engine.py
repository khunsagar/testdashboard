"""
Rule Engine — matches the whiteboard's decision node between triggers
and the backend service.

Step 6: implement real rules, e.g.:
    branch in ("master", "main") or event == "pull_request" -> run E2E, API, Regression
    branch startswith "feature/" and event == "push"        -> run unit tests only

Keep this a pure function (no DB, no I/O) so it's trivially unit-testable
in isolation, per the "every feature must include unit tests" rule.
"""

from dataclasses import dataclass


@dataclass
class RuleDecision:
    test_types: list[str]
    reason: str


def evaluate(branch: str | None, event: str | None) -> RuleDecision:
    """Placeholder logic — replace with real rules in Step 6."""
    if branch in ("master", "main") or event == "pull_request":
        return RuleDecision(test_types=["e2e", "api", "regression"], reason="protected branch or PR")

    if event == "push":
        return RuleDecision(test_types=["unit"], reason="feature branch push")

    return RuleDecision(test_types=["smoke"], reason="default fallback")
