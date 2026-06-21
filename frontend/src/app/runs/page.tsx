"use client";

import { useEffect, useMemo, useState } from "react";
import { RunDetail } from "@/components/run-detail";
import { RunTable } from "@/components/run-table";
import { TaskForm } from "@/components/task-form";
import { api } from "@/lib/api";
import type { TaskRun } from "@/lib/types";

export default function TaskStudioPage() {
  const [runs, setRuns] = useState<TaskRun[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function refresh(preferredId?: string) {
    try {
      const response = await api.listRuns();
      setRuns(response.items);
      setSelectedId((current) => preferredId ?? current ?? response.items[0]?.id ?? null);
      setError(null);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Could not load task runs.");
    }
  }

  useEffect(() => {
    const preferredId = new URLSearchParams(window.location.search).get("selected") ?? undefined;
    void refresh(preferredId);
  }, []);

  const selectedRun = useMemo(() => runs.find((run) => run.id === selectedId) ?? runs[0] ?? null, [runs, selectedId]);

  async function review(
    decision: "approve" | "reject" | "request_changes",
    reviewer: string,
    comment: string
  ) {
    if (!selectedRun) return;
    try {
      const updated = await api.reviewRun(selectedRun.id, { decision, reviewer, comment });
      setRuns((current) => current.map((run) => run.id === updated.id ? updated : run));
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Could not record review.");
    }
  }

  return (
    <div className="page-container">
      <header className="page-header">
        <div><p className="eyebrow">Power-user workspace</p><h1>Task studio</h1><p className="header-copy">Turn a complex objective into a review-ready decision brief with an auditable evidence trail.</p></div>
      </header>
      {error ? <div className="error-banner">{error}</div> : null}
      <section className="panel"><p className="eyebrow">New governed task</p><TaskForm onCreated={async (run) => { await refresh(run.id); }} /></section>
      <section className="panel"><div className="section-heading"><div><p className="eyebrow">Execution history</p><h2>Runs</h2></div></div><RunTable runs={runs} /></section>
      {selectedRun ? <RunDetail run={selectedRun} onReview={review} /> : null}
    </div>
  );
}
