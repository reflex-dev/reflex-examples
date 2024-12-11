"""Custom Exceptions."""


class ReflexHostingCliError(Exception):
    """Base exception for all Reflex Hosting CLI exceptions."""


class NotAuthenticatedError(ReflexHostingCliError):
    """Raised when the user is not authenticated."""
