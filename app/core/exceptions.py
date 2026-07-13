"""
Custom exception types for the platform, so services/repositories can raise
domain-specific errors instead of generic ones — the API layer catches these
and maps them to proper HTTP responses (see app/core/exception_handlers.py,
to be added when Phase 4 REST APIs are built).
"""


class TestControlError(Exception):
    """Base class for all domain-specific errors in this app."""


class ExecutionNotFoundError(TestControlError):
    """Raised when an execution ID doesn't exist."""


class InvalidRuleConfigError(TestControlError):
    """Raised when the rule engine gets a config it can't evaluate."""


class GitHubIntegrationError(TestControlError):
    """Raised when a call to the GitHub API or webhook parsing fails."""
