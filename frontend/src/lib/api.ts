import type {
  DashboardSummary,
  EvaluationCase,
  EvaluationRun,
  ModelProfile,
  ModelProfileName,
  TaskRun
} from "@/lib/types";

const API_ROOT = (process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000").replace(/\/$/, "");
const API_PREFIX = `${API_ROOT}/api/v1`;

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_PREFIX}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      "X-Tenant-ID": "demo-tenant",
      ...(init?.headers ?? {})
    },
    cache: "no-store"
  });
  if (!response.ok) {
    const payload = await response.json().catch(() => ({ detail: response.statusText }));
    throw new ApiError(response.status, String(payload.detail ?? "Unexpected API error"));
  }
  return response.json() as Promise<T>;
}

export const api = {
  getDashboard: () => request<DashboardSummary>("/dashboard/summary"),
  listRuns: () => request<{ items: TaskRun[]; total: number }>("/tasks/runs"),
  getRun: (runId: string) => request<TaskRun>(`/tasks/runs/${runId}`),
  createRun: (payload: { title: string; request: string; model_profile: ModelProfileName }) =>
    request<TaskRun>("/tasks/runs", { method: "POST", body: JSON.stringify(payload) }),
  reviewRun: (runId: string, payload: { decision: string; reviewer: string; comment: string }) =>
    request<TaskRun>(`/tasks/runs/${runId}/review`, { method: "POST", body: JSON.stringify(payload) }),
  getProfiles: () => request<ModelProfile[]>("/evaluations/model-profiles"),
  getCases: () => request<EvaluationCase[]>("/evaluations/cases"),
  runEvaluation: (payload: { model_profiles: ModelProfileName[]; task_ids?: string[] }) =>
    request<EvaluationRun>("/evaluations/runs", { method: "POST", body: JSON.stringify(payload) })
};

export { ApiError };
