import type {
  RecommendRequest,
  RecommendResponse,
  FeedbackSubmit,
  HistoryResponse,
  PublicFeedbackResponse,
} from "../types/distro";

const BASE = "/api";

export async function recommend(
  req: RecommendRequest,
): Promise<RecommendResponse> {
  const res = await fetch(`${BASE}/recommend`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ message: `API error: ${res.status}` }));
    throw new Error(err.message || err.error || `API error: ${res.status}`);
  }
  return res.json();
}

export async function submitFeedback(
  data: FeedbackSubmit,
): Promise<void> {
  const res = await fetch(`${BASE}/feedback`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ message: `Feedback error: ${res.status}` }));
    throw new Error(err.message || err.error || `Feedback error: ${res.status}`);
  }
}

export async function getHistory(): Promise<HistoryResponse> {
  const res = await fetch(`${BASE}/feedback/history`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ message: `History error: ${res.status}` }));
    throw new Error(err.message || err.error || `History error: ${res.status}`);
  }
  return res.json();
}

export async function getPublicFeedback(): Promise<PublicFeedbackResponse> {
  const res = await fetch(`${BASE}/feedback/public`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ message: `Public feedback error: ${res.status}` }));
    throw new Error(err.message || err.error || `Public feedback error: ${res.status}`);
  }
  return res.json();
}
