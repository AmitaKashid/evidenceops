from __future__ import annotations

import hashlib
import re
from collections.abc import Mapping
from typing import Any

SENSITIVE_KEY_PATTERN = re.compile(r"(api[_-]?key|token|secret|password|authorization)", re.I)


def stable_hash(value: str) -> str:
    """Return a short stable hash for correlation without retaining raw content."""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def redact_payload(value: Any) -> Any:
    """Redact likely secrets recursively before telemetry persistence."""
    if isinstance(value, Mapping):
        result: dict[str, Any] = {}
        for key, item in value.items():
            if SENSITIVE_KEY_PATTERN.search(str(key)):
                result[str(key)] = "[REDACTED]"
            else:
                result[str(key)] = redact_payload(item)
        return result
    if isinstance(value, list):
        return [redact_payload(item) for item in value]
    if isinstance(value, str) and len(value) > 1500:
        return {"preview": value[:240] + "…", "sha256": stable_hash(value), "length": len(value)}
    return value


def require_same_tenant(resource_tenant_id: str, request_tenant_id: str) -> None:
    if resource_tenant_id != request_tenant_id:
        raise PermissionError("Resource does not belong to the active tenant.")
