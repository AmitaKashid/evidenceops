import type { ReactNode } from "react";

export function MetricCard({
  label,
  value,
  detail,
  tone = "default",
  icon
}: {
  label: string;
  value: string | number;
  detail: string;
  tone?: "default" | "positive" | "warning" | "danger";
  icon?: ReactNode;
}) {
  return (
    <article className={`metric-card metric-${tone}`}>
      <div className="metric-topline">
        <span>{label}</span>
        {icon ? <span className="metric-icon">{icon}</span> : null}
      </div>
      <strong>{value}</strong>
      <small>{detail}</small>
    </article>
  );
}
