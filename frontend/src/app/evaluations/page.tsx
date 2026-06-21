"use client";

import { useEffect, useMemo, useState } from "react";

import { ScoreBar } from "@/components/score-bar";
import { api } from "@/lib/api";
import type { EvaluationCase, EvaluationRun, ModelProfile, ModelProfileName } from "@/lib/types";

const defaults: ModelProfileName[] = ["enterprise-fast", "enterprise-balanced", "enterprise-precise"];

export default function EvaluationsPage() {
  const [profiles, setProfiles] = useState<ModelProfile[]>([]);
  const [cases, setCases] = useState<EvaluationCase[]>([]);
  const [selectedProfiles, setSelectedProfiles] = useState<ModelProfileName[]>(defaults);
  const [latest, setLatest] = useState<EvaluationRun | null>(null);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([api.getProfiles(), api.getCases()])
      .then(([profileResponse, caseResponse]) => { setProfiles(profileResponse); setCases(caseResponse); })
      .catch((caught: Error) => setError(caught.message));
  }, []);

  const grouped = useMemo(() => {
    const map = new Map<string, EvaluationRun["results"]>();
    latest?.results.forEach((result) => {
      const values = map.get(result.model_profile) ?? [];
      values.push(result);
      map.set(result.model_profile, values);
    });
    return map;
  }, [latest]);

  function toggleProfile(profile: ModelProfileName) {
    setSelectedProfiles((current) => current.includes(profile) ? current.filter((item) => item !== profile) : [...current, profile]);
  }

  async function runTaskBench() {
    if (!selectedProfiles.length) return;
    setRunning(true);
    setError(null);
    try {
      setLatest(await api.runEvaluation({ model_profiles: selectedProfiles }));
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Evaluation failed.");
    } finally {
      setRunning(false);
    }
  }

  return (
    <div className="page-container">
      <header className="page-header"><div><p className="eyebrow">Continuous improvement</p><h1>Evaluation lab</h1><p className="header-copy">Replay versioned tasks, compare configured policies fairly, and turn operational failures into regression gates.</p></div></header>
      {error ? <div className="error-banner">{error}</div> : null}
      <section className="three-column-section">
        {profiles.map((profile) => (
          <article className={`profile-card ${selectedProfiles.includes(profile.name) ? "selected" : ""}`} key={profile.name}>
            <label className="checkbox-label"><input type="checkbox" checked={selectedProfiles.includes(profile.name)} onChange={() => toggleProfile(profile.name)} /> Include</label>
            <h2>{profile.name}</h2>
            <p>{profile.description}</p>
            <dl><div><dt>Quality bias</dt><dd>{Math.round(profile.quality_bias * 100)}%</dd></div><div><dt>Cost index</dt><dd>{profile.cost_index}×</dd></div><div><dt>Latency target</dt><dd>{profile.latency_target_ms} ms</dd></div></dl>
            <small>{profile.intended_use}</small>
          </article>
        ))}
      </section>
      <section className="panel benchmark-action"><div><p className="eyebrow">TaskBench</p><h2>{cases.length} versioned reliability cases</h2><p>Grounding, cross-document reasoning, numeric reconciliation, incomplete evidence, and adversarial instruction handling.</p></div><button className="button button-primary" disabled={running || !selectedProfiles.length} onClick={runTaskBench}>{running ? "Running benchmark…" : "Run selected profiles"}</button></section>
      <section className="panel"><p className="eyebrow">Evaluation catalogue</p><div className="case-list">{cases.map((item) => <article key={item.task_id}><div><code>{item.task_id}</code><h3>{item.title}</h3><p>{item.prompt}</p></div><div className="tag-list">{item.tags.map((tag) => <span key={tag}>{tag}</span>)}</div></article>)}</div></section>
      {latest ? <section className="panel"><div className="section-heading"><div><p className="eyebrow">Latest run</p><h2>Comparison results</h2></div><span className="section-note">{latest.summary?.best_profile ? `Best policy: ${latest.summary.best_profile}` : latest.summary?.comparison_mode ?? "No comparative winner"}</span></div><div className="comparison-grid">{Array.from(grouped.entries()).map(([profile, items]) => { const average = (key: "composite_score" | "task_completion" | "citation_coverage" | "numeric_accuracy") => items.reduce((total, item) => total + item[key], 0) / Math.max(items.length, 1); return <article className="comparison-card" key={profile}><h3>{profile}</h3><ScoreBar label="Composite score" value={average("composite_score")} intent={average("composite_score") > 0.8 ? "positive" : "warning"} /><ScoreBar label="Task completion" value={average("task_completion")} /><ScoreBar label="Citation coverage" value={average("citation_coverage")} /><ScoreBar label="Numeric accuracy" value={average("numeric_accuracy")} intent="positive" /><p className="muted-note">Mean latency {Math.round(items.reduce((total, item) => total + item.latency_ms, 0) / items.length)} ms · Estimated run cost ${items.reduce((total, item) => total + item.estimated_cost_usd, 0).toFixed(3)}</p></article>; })}</div><div className="table-shell"><table><thead><tr><th>Task</th><th>Policy</th><th>Completion</th><th>Evidence</th><th>Numeric</th><th>Escalation</th><th>Score</th></tr></thead><tbody>{latest.results.map((result) => <tr key={`${result.task_id}-${result.model_profile}`}><td>{result.task_id}</td><td><code>{result.model_profile}</code></td><td>{Math.round(result.task_completion * 100)}%</td><td>{Math.round(result.citation_coverage * 100)}%</td><td>{Math.round(result.numeric_accuracy * 100)}%</td><td>{Math.round(result.escalation_correctness * 100)}%</td><td><strong>{Math.round(result.composite_score * 100)}%</strong></td></tr>)}</tbody></table></div></section> : null}
    </div>
  );
}
