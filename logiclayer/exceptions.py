"""LogicLayer errors and exceptions module.

Contains the errors and exceptions the code can raise at some point during
execution.
"""


class BaseError(Exception):
    """Base Error class for all errors in the module."""


class HealthCheckError(BaseError):
    """At least one of the healthchecks set in the LogicLayer instance failed."""
