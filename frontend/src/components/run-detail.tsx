"use client";

import { useState } from "react";

import { ScoreBar } from "@/components/score-bar";
import { StatusBadge } from "@/components/status-badge";
import type { TaskRun } from "@/lib/types";

export function RunDetail({ run, onReview }: {
  run: TaskRun;
  onReview: (
    decision: "approve" | "reject" | "request_changes",
    reviewer: string,
    comment: string
  ) => Promise<void>;
}) {
  const [reviewer, setReviewer] = useState("Portfolio reviewer");
  const [comment, setComment] = useState("");
  const [reviewing, setReviewing] = useState(false);

  async function submitReview(decision: "approve" | "reject" | "request_changes") {
    setReviewing(true);
    try {
      await onReview(decision, reviewer, comment);
    } finally {
      setReviewing(false);
    }
  }

  if (!run.decision_brief || !run.verification) {
    return <div className="empty-state">The selected run has not generated a decision brief.</div>;
  }
  const brief = run.decision_brief;
  const verification = run.verification;
  return (
    <div className="run-detail">
      <section className="panel detail-header">
        <div>
          <p className="eyebrow">Task execution</p>
          <h2>{run.title}</h2>
          <p>{run.request}</p>
        </div>
        <div className="detail-meta">
          <StatusBadge status={run.status} />
          <code>{run.model_profile}</code>
        </div>
      </section>

      <section className="detail-grid">
        <article className="panel brief-panel">
          <p className="eyebrow">Decision brief</p>
          <h3>{brief.recommendation}</h3>
          <p className="lead-copy">{brief.executive_summary}</p>
          <h4>Rationale</h4>
          <ul>{brief.rationale.map((item) => <li key={item}>{item}</li>)}</ul>
          <h4>Trade-offs and caveats</h4>
          <ul>{brief.tradeoffs.map((item) => <li key={item}>{item}</li>)}</ul>
          <h4>Assumptions</h4>
          <ul>{brief.assumptions.map((item) => <li key={item}>{item}</li>)}</ul>
          <h4>Required next actions</h4>
          <ul>{brief.next_actions.map((item) => <li key={item}>{item}</li>)}</ul>
        </article>

        <aside className="panel verification-panel">
          <p className="eyebrow">Verification ledger</p>
          <h3>{Math.round(verification.quality_score * 100)}% quality score</h3>
          <ScoreBar label="Evidence coverage" value={verification.citation_coverage} />
          <ScoreBar label="Citation precision" value={verification.citation_precision} />
          <ScoreBar label="Numeric reconciliation" value={verification.numeric_accuracy} intent={verification.numeric_accuracy < 1 ? "warning" : "positive"} />
          <div className={`verdict ${verification.passed ? "verdict-pass" : "verdict-fail"}`}>
            {verification.passed ? "No blocking verification errors" : "Blocking validation issue detected"}
          </div>
          <ul className="issues-list">
            {verification.issues.length ? verification.issues.map((issue) => (
              <li key={`${issue.rule_id}-${issue.message}`}>
                <strong>{issue.severity}</strong> · {issue.message}
                {issue.remediation ? <small>{issue.remediation}</small> : null}
              </li>
            )) : <li>No additional verifier issues were recorded.</li>}
          </ul>
        </aside>
      </section>

      <section className="panel">
        <p className="eyebrow">Evidence ledger</p>
        <div className="claims-grid">
          {brief.claims.map((claim) => (
            <article className="claim-card" key={claim.claim_id}>
              <span className="claim-label">{claim.importance} claim</span>
              <p>{claim.statement}</p>
              <div className="citation-list">
                {claim.citations.map((citation) => (
                  <details key={citation.chunk_id}>
                    <summary>{citation.title} · {citation.section} · score {Math.round(citation.score * 100)}%</summary>
                    <p>{citation.excerpt}</p>
                  </details>
                ))}
              </div>
            </article>
          ))}
        </div>
      </section>

      <section className="panel">
        <p className="eyebrow">Human approval gate</p>
        {run.status === "waiting_for_review" ? (
          <div className="review-gate">
            <label>
              Reviewer name
              <input value={reviewer} onChange={(event) => setReviewer(event.target.value)} />
            </label>
            <label>
              Review note
              <textarea rows={3} value={comment} onChange={(event) => setComment(event.target.value)} placeholder="Record the basis for the decision." />
            </label>
            <div className="review-actions">
              <button className="button button-secondary" disabled={reviewing} onClick={() => submitReview("request_changes")}>Request changes</button>
              <button className="button button-danger" disabled={reviewing} onClick={() => submitReview("reject")}>Reject</button>
              <button className="button button-primary" disabled={reviewing} onClick={() => submitReview("approve")}>Approve decision brief</button>
            </div>
          </div>
        ) : (
          <p className="review-record">{run.review ? `${run.review.decision} by ${run.review.reviewer}: ${run.review.comment || "No comment provided."}` : "No reviewer action is required for this run."}</p>
        )}
      </section>

      <section className="panel">
        <p className="eyebrow">Execution trace</p>
        <ol className="timeline">
          {run.events.map((event) => (
            <li key={`${event.sequence}-${event.event_type}`}>
              <span className="timeline-sequence">{String(event.sequence).padStart(2, "0")}</span>
              <div>
                <strong>{event.stage}</strong>
                <small>{event.event_type}</small>
                <code>{JSON.stringify(event.payload)}</code>
              </div>
            </li>
          ))}
        </ol>
      </section>
    </div>
  );
}
