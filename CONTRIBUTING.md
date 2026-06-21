# Contributing

## Development principles

1. Add an evaluation case before changing workflow behavior that affects reliability.
2. Keep agent nodes narrow, typed, and independently testable.
3. Do not add hidden external side effects to the default workflow.
4. Redact or hash sensitive values before placing them in operational telemetry.
5. Keep all customer-facing claims linked to evidence or explicitly marked as assumptions.

## Pull request checklist

- [ ] Unit tests cover new logic.
- [ ] A TaskBench case exists for a repaired production-like failure.
- [ ] `pytest`, Ruff, mypy, and frontend type checks pass.
- [ ] Documentation identifies operational impact and any new data flow.
- [ ] No secrets, raw customer data, or hidden API keys are committed.
