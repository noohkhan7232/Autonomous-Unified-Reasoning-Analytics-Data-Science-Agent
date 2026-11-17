export type Dataset = {
  id: string; name: string; size: number; rows: number; columns: number; created: string;
  last_analyzed?: string; schema?: { name: string; dtype: string; missing: number; unique: number; examples: unknown[] }[];
};
export type Run = {
  id: string; dataset_id: string; dataset: string; created: string; status: string;
  model?: string; score?: number; model_f1?: number; verdict?: string;
};
export type Metrics = Record<string, number>;
export type Results = {
  eda?: { numeric_summary: Record<string, Metrics>; missing_values: Metrics; target_distribution: Metrics };
  modeling?: { best_model: string; model_comparison: Record<string, Metrics> };
  evaluation?: { data_quality_score: number; model_quality_score: number; system_score: number; verdict: string; issues: string[]; recommendations: string[] };
  explanation_status?: string;
  sources?: { document: string; page: number | null; excerpt: string }[];
};
export type RunDetail = Run & { config: { target: string; test_size: number; random_state: number }; results: Results; report: string };
export type RunEvent = { id: number; stage: string; status: string; detail: string; time: string };
export type Profile = { memory: number; duplicates: number; missing: number; numeric: Record<string, Metrics>; categorical: Record<string, Metrics>; correlations: Record<string, Metrics>; histograms: Record<string, Metrics> };
export type Preview = { total: number; rows: unknown[][] };

export async function api<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch("/api/" + path, options);
  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    const detail = payload?.detail;
    throw new Error(typeof detail === "string" ? detail : Array.isArray(detail) ? detail.map((item: { msg: string }) => item.msg).join(" · ") : "Request failed (" + response.status + ").");
  }
  return response.status === 204 ? undefined as T : response.json();
}

export function modelName(name: string) {
  return name.replaceAll("_", " ").replace(/\b\w/g, char => char.toUpperCase());
}
export const date = (stamp?: string) => stamp ? new Date(stamp).toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" }) : "—";
export const percent = (score?: number | null) => score == null ? "—" : (score * 100).toFixed(1) + "%";
