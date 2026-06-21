from __future__ import annotations

import json
from pathlib import Path

from app.domain.schemas import EvaluationCase


class TaskBenchRepository:
    def __init__(self, taskbench_path: Path) -> None:
        self.taskbench_path = taskbench_path

    def list_cases(self) -> list[EvaluationCase]:
        raw = json.loads(self.taskbench_path.read_text(encoding="utf-8"))
        return [EvaluationCase.model_validate(item) for item in raw]

    def select(self, task_ids: list[str]) -> list[EvaluationCase]:
        cases = self.list_cases()
        if not task_ids:
            return cases
        requested = set(task_ids)
        selected = [case for case in cases if case.task_id in requested]
        missing = requested.difference(case.task_id for case in selected)
        if missing:
            raise ValueError(f"Unknown TaskBench ids: {sorted(missing)}")
        return selected
