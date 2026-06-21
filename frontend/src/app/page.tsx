"use client";

import { useEffect, useState } from "react";

import { MetricCard } from "@/components/metric-card";
import { RunTable } from "@/components/run-table";
import { ScoreBar } from "@/components/score-bar";
import { api } from "@/lib/api";
import type { DashboardSummary } from "@/lib/types";

export default function ControlRoomPage() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.getDashboard().then(setSummary).catch((caught: Error) => setError(caught.message));
  }, []);

  const profiles = summary?.latest_evaluation_summary?.profiles ?? {};
  return (
    <div className="page-container">
      <header className="page-header">
        <div>
          <p className="eyebrow">Governed task execution</p>
          <h1>Control room</h1>
          <p className="header-copy">Operate complex decision workflows with source validation, deterministic controls, human approval, and evaluation evidence.</p>
        </div>
        <div className="header-callout"><span className="status-dot" /> Evidence-first · Read-only · Tenant scoped</div>
      </header>

      {error ? <div className="error-banner">Backend unavailable: {error}. Start the FastAPI service at port 8000.</div> : null}
      <section className="metric-grid">
        <MetricCard label="Workflow runs" value={summary?.total_runs ?? "—"} detail="Persisted task executions" />
        <MetricCard label="Review queue" value={summary?.waiting_for_review ?? "—"} detail="Human approval required" tone="warning" />
        <MetricCard label="Average quality" value={summary ? `${Math.round(summary.average_quality_score * 100)}%` : "—"} detail="Verifier-derived run score" tone="positive" />
        <MetricCard label="Open issues" value={summary?.open_verification_issues ?? "—"} detail="Warnings and validation gaps" tone={(summary?.open_verification_issues ?? 0) > 0 ? "warning" : "default"} />
      </section>

      <section className="two-column-section">
        <article className="panel">
          <div className="section-heading">
            <div><p className="eyebrow">Operational queue</p><h2>Recent decision runs</h2></div>
            <span className="section-note">Every output retains a trace and review state.</span>
          </div>
          <RunTable runs={summary?.recent_runs ?? []} />
        </article>
        <aside className="panel">
          <p className="eyebrow">Model policy evidence</p>
          <h2>Latest evaluation snapshot</h2>
          {Object.keys(profiles).length ? (
            <div className="profile-score-list">
              {Object.entries(profiles).map(([profile, metrics]) => (
                <div className="profile-score" key={profile}>
                  <div><strong>{profile}</strong><small>{Math.round(metrics.latency_ms)} ms mean latency · ${metrics.estimated_cost_usd.toFixed(3)} run estimate</small></div>
                  <ScoreBar label="Composite reliability" value={metrics.composite_score} intent={metrics.composite_score >= 0.8 ? "positive" : "warning"} />
                </div>
              ))}
              <p className="muted-note">{summary?.latest_evaluation_summary?.best_profile ? <>Best profile: <strong>{summary.latest_evaluation_summary.best_profile}</strong>.</> : "No quality winner is declared while profiles share the local deterministic provider."} This dashboard compares configured policies, not universal model rankings.</p>
            </div>
          ) : <div className="empty-state">Run the TaskBench in Evaluation Lab to populate model-policy evidence.</div>}
        </aside>
      </section>

      <section className="control-principles">
        <article><span>01</span><h3>Bounded delegation</h3><p>The system carries out a typed task graph, not unbounded autonomous loops.</p></article>
        <article><span>02</span><h3>Evidence ledger</h3><p>Material claims must reference retrieved sources and are shown to the reviewer.</p></article>
        <article><span>03</span><h3>Regression culture</h3><p>TaskBench turns workflow failures into replayable evaluation cases.</p></article>
      </section>
    </div>
  );
}
