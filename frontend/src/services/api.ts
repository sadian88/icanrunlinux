import type { RecommendRequest, RecommendResult } from "../types/distro";

const BASE = "/api";

export async function recommend(
  req: RecommendRequest,
): Promise<RecommendResult[]> {
  const res = await fetch(`${BASE}/recommend`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}
