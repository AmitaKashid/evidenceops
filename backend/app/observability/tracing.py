from __future__ import annotations

import time
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from app.core.config import Settings
from app.core.security import redact_payload


class WorkflowTracer:
    """OpenTelemetry wrapper plus safe event timing helpers.

    Run-level events are persisted in the database by the orchestration layer.
    OpenTelemetry is used for external trace export when configured.
    """

    def __init__(self, settings: Settings) -> None:
        resource = Resource.create({"service.name": settings.otel_service_name})
        provider = TracerProvider(resource=resource)
        if settings.otel_exporter_otlp_endpoint:
            exporter = OTLPSpanExporter(endpoint=f"{settings.otel_exporter_otlp_endpoint.rstrip('/')}/v1/traces")
            provider.add_span_processor(BatchSpanProcessor(exporter))
        # This local provider is intentionally isolated for the demo. It does not
        # export spans unless an OTLP collector endpoint is explicitly configured.
        self.provider = provider
        self.tracer = provider.get_tracer("evidenceops.workflow")
        self.store_redacted_payloads = settings.store_redacted_trace_payloads

    @contextmanager
    def stage(self, name: str, attributes: dict[str, Any] | None = None) -> Generator[dict[str, Any], None, None]:
        start = time.perf_counter()
        safe_attributes = redact_payload(attributes or {}) if self.store_redacted_payloads else {}
        with self.tracer.start_as_current_span(name) as span:
            for key, value in safe_attributes.items():
                span.set_attribute(str(key), str(value))
            result: dict[str, Any] = {}
            try:
                yield result
                span.set_attribute("evidenceops.stage.outcome", "success")
            except Exception as exc:
                span.record_exception(exc)
                span.set_attribute("evidenceops.stage.outcome", "error")
                raise
            finally:
                result["latency_ms"] = int((time.perf_counter() - start) * 1000)
                span.set_attribute("evidenceops.stage.latency_ms", result["latency_ms"])
