import Link from "next/link";

import { StatusBadge } from "@/components/status-badge";
import type { TaskRun } from "@/lib/types";

function formatDate(value: string) {
  return new Intl.DateTimeFormat("en-GB", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));
}

export function RunTable({ runs }: { runs: TaskRun[] }) {
  if (!runs.length) {
    return <div className="empty-state">No workflow runs exist yet. Open Task Studio to create the first decision brief.</div>;
  }
  return (
    <div className="table-shell">
      <table>
        <thead>
          <tr>
            <th>Decision task</th>
            <th>Model policy</th>
            <th>Quality</th>
            <th>Status</th>
            <th>Updated</th>
          </tr>
        </thead>
        <tbody>
          {runs.map((run) => (
            <tr key={run.id}>
              <td>
                <Link href={`/runs?selected=${run.id}`} className="table-primary">
                  {run.title}
                </Link>
                <span className="table-secondary">{run.request.slice(0, 82)}{run.request.length > 82 ? "…" : ""}</span>
              </td>
              <td><code>{run.model_profile}</code></td>
              <td>{run.verification ? `${Math.round(run.verification.quality_score * 100)}%` : "—"}</td>
              <td><StatusBadge status={run.status} /></td>
              <td>{formatDate(run.updated_at)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
