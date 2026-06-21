export function ScoreBar({ label, value, intent = "default" }: { label: string; value: number; intent?: "default" | "positive" | "warning" }) {
  const percentage = Math.max(0, Math.min(100, Math.round(value * 100)));
  return (
    <div className="score-row">
      <div className="score-label">
        <span>{label}</span>
        <strong>{percentage}%</strong>
      </div>
      <div className="score-track" aria-label={`${label}: ${percentage}%`}>
        <span className={`score-fill score-${intent}`} style={{ width: `${percentage}%` }} />
      </div>
    </div>
  );
}
