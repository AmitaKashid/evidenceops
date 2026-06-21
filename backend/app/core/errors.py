class EvidenceOpsError(Exception):
    """Base class for expected domain errors."""


class NotFoundError(EvidenceOpsError):
    """Raised when a requested resource does not exist for the current tenant."""


class ValidationFailure(EvidenceOpsError):
    """Raised when a task cannot satisfy its structured contract."""


class PolicyViolation(EvidenceOpsError):
    """Raised when a requested action violates the local governance policy."""
