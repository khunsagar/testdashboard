"""
Parses inbound GitHub webhook payloads (workflow_run events) per the
whiteboard's "hybrid approach" — this is the authoritative lifecycle
event source, separate from the workflow's own start/finish calls.

Phase 6. Verify payload signature using settings.github_webhook_secret
before trusting any payload.
"""


def parse_workflow_run_event(payload: dict) -> dict:
    """Extract the fields we care about from a workflow_run webhook payload."""
    raise NotImplementedError
