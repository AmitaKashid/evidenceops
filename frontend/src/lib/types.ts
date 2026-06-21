export type RunStatus = "queued" | "running" | "waiting_for_review" | "approved" | "rejected" | "failed";
export type ModelProfileName = "enterprise-fast" | "enterprise-balanced" | "enterprise-precise";

export interface SourceReference {
  document_id: string;
  chunk_id: string;
  title: string;
  section: string;
  excerpt: string;
  score: number;
  source_type: "internal" | "pricing" | "public_research";
}

export interface DecisionClaim {
  claim_id: string;
  statement: string;
  importance: "material" | "supporting";
  citations: SourceReference[];
  numeric_values: Record<string, number>;
  confidence: number;
}

export interface DecisionBrief {
  executive_summary: string;
  recommendation: string;
  rationale: string[];
  tradeoffs: string[];
  findings: Array<{
    finding_id: string;
    category: string;
    title: string;
    statement: string;
    severity: "info" | "low" | "medium" | "high";
    evidence: SourceReference[];
    confidence: number;
    requires_review: boolean;
  }>;
  claims: DecisionClaim[];
  assumptions: string[];
  unresolved_questions: string[];
  next_actions: string[];
  generated_by: string;
}

export interface VerificationResult {
  passed: boolean;
  quality_score: number;
  citation_coverage: number;
  citation_precision: number;
  numeric_accuracy: number;
  escalation_required: boolean;
  issues: Array<{
    rule_id: string;
    severity: "info" | "warning" | "error";
    message: string;
    claim_id?: string | null;
    evidence_ids: string[];
    remediation?: string | null;
  }>;
}

export interface RunEvent {
  sequence: number;
  event_type: string;
  stage: string;
  payload: Record<string, unknown>;
  created_at: string;
}

export interface TaskRun {
  id: string;
  tenant_id: string;
  title: string;
  request: string;
  model_profile: ModelProfileName;
  status: RunStatus;
  created_at: string;
  updated_at: string;
  decision_brief?: DecisionBrief | null;
  verification?: VerificationResult | null;
  review?: {
    decision: "approve" | "reject" | "request_changes";
    reviewer: string;
    comment: string;
    reviewed_at: string;
  } | null;
  events: RunEvent[];
}

export interface DashboardSummary {
  total_runs: number;
  waiting_for_review: number;
  approval_rate: number;
  average_quality_score: number;
  average_latency_ms: number;
  open_verification_issues: number;
  latest_evaluation_summary?: {
    total_cases?: number;
    best_profile?: string | null;
    comparison_mode?: string;
    profiles?: Record<string, {
      composite_score: number;
      task_completion: number;
      citation_coverage: number;
      numeric_accuracy: number;
      latency_ms: number;
      estimated_cost_usd: number;
    }>;
  } | null;
  recent_runs: TaskRun[];
}

export interface ModelProfile {
  name: ModelProfileName;
  description: string;
  quality_bias: number;
  cost_index: number;
  latency_target_ms: number;
  intended_use: string;
}

export interface EvaluationCase {
  task_id: string;
  title: string;
  prompt: string;
  expected_vendor?: string | null;
  expected_claim_fragments: string[];
  expected_document_ids: string[];
  expected_escalation: boolean;
  tags: string[];
}

export interface EvaluationResult {
  task_id: string;
  model_profile: ModelProfileName;
  task_completion: number;
  citation_coverage: number;
  numeric_accuracy: number;
  escalation_correctness: number;
  latency_ms: number;
  estimated_cost_usd: number;
  composite_score: number;
  notes: string[];
}

export interface EvaluationRun {
  id: string;
  tenant_id: string;
  status: string;
  started_at: string;
  completed_at?: string | null;
  configuration: Record<string, unknown>;
  summary: DashboardSummary["latest_evaluation_summary"];
  results: EvaluationResult[];
}
