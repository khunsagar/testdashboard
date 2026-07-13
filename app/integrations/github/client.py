"""
GitHub REST API client (Phase 6). Handles: OAuth token exchange,
workflow_dispatch calls, workflow status sync.

Kept separate from webhook parsing (see webhook_handler.py) because
one is outbound (we call GitHub) and the other is inbound (GitHub calls us).
"""


class GitHubClient:
    def __init__(self, token: str):
        self.token = token

    def trigger_workflow(self, repo: str, workflow_id: str, ref: str, inputs: dict) -> None:
        """Calls GitHub's workflow_dispatch API. Not yet implemented."""
        raise NotImplementedError

    def get_workflow_run_status(self, repo: str, run_id: str) -> dict:
        """Fetches current status of a workflow run. Not yet implemented."""
        raise NotImplementedError
