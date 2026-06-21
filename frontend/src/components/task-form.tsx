"use client";

import { FormEvent, useState } from "react";

import type { ModelProfileName, TaskRun } from "@/lib/types";

const DEFAULT_PROMPT = "Review the approved vendor documents, compare all vendors against the internal security requirements, calculate a three-year total cost of ownership, identify policy gaps, and prepare a management decision brief with evidence citations. Escalate any unsupported conclusion.";

export function TaskForm({ onCreated }: { onCreated: (run: TaskRun) => Promise<void> | void }) {
  const [title, setTitle] = useState("Vendor selection decision brief");
  const [request, setRequest] = useState(DEFAULT_PROMPT);
  const [modelProfile, setModelProfile] = useState<ModelProfileName>("enterprise-balanced");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      const response = await fetch(`${(process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000").replace(/\/$/, "")}/api/v1/tasks/runs`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-Tenant-ID": "demo-tenant" },
        body: JSON.stringify({ title, request, model_profile: modelProfile })
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail ?? "Task execution failed.");
      await onCreated(payload as TaskRun);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Task execution failed.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form className="task-form" onSubmit={onSubmit}>
      <div className="field-grid">
        <label>
          Task title
          <input value={title} onChange={(event) => setTitle(event.target.value)} minLength={6} maxLength={160} required />
        </label>
        <label>
          Model policy
          <select value={modelProfile} onChange={(event) => setModelProfile(event.target.value as ModelProfileName)}>
            <option value="enterprise-fast">Enterprise fast</option>
            <option value="enterprise-balanced">Enterprise balanced</option>
            <option value="enterprise-precise">Enterprise precise</option>
          </select>
        </label>
      </div>
      <label>
        Decision objective
        <textarea value={request} onChange={(event) => setRequest(event.target.value)} rows={8} minLength={25} maxLength={6000} required />
      </label>
      <div className="form-footer">
        <p>The workflow uses approved sources, deterministic calculation, source validation, and a human-review gate.</p>
        <button className="button button-primary" disabled={submitting} type="submit">
          {submitting ? "Executing workflow…" : "Create decision brief"}
        </button>
      </div>
      {error ? <p className="form-error">{error}</p> : null}
    </form>
  );
}
