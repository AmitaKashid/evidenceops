import type { RunStatus } from "@/lib/types";

const labels: Record<RunStatus, string> = {
  queued: "Queued",
  running: "Running",
  waiting_for_review: "Review required",
  approved: "Approved",
  rejected: "Rejected",
  failed: "Failed"
};

export function StatusBadge({ status }: { status: RunStatus }) {
  return <span className={`status-badge status-${status}`}>{labels[status]}</span>;
}
