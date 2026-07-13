"""
Rule Engine unit tests — pure function, no DB, no HTTP.
This is the pattern to follow for every new rule added in Step 6.
"""

from app.rule_engine.engine import evaluate


def test_master_branch_runs_full_suite():
    decision = evaluate(branch="master", event="push")
    assert decision.test_types == ["e2e", "api", "regression"]


def test_pull_request_runs_full_suite():
    decision = evaluate(branch="feature/login", event="pull_request")
    assert decision.test_types == ["e2e", "api", "regression"]


def test_feature_branch_push_runs_unit_only():
    decision = evaluate(branch="feature/login", event="push")
    assert decision.test_types == ["unit"]


def test_unknown_trigger_falls_back_to_smoke():
    decision = evaluate(branch=None, event=None)
    assert decision.test_types == ["smoke"]
