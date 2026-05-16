import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowLeft, Star, MessageSquare, Search } from "lucide-react";
import type { PublicFeedbackEntry } from "../types/distro";
import { getPublicFeedback } from "../services/api";

const ARCH_BLUE = "#1793D1";

function formatDate(d: string | null): string {
  if (!d) return "—";
  return new Date(d).toLocaleString();
}

function requestSummary(data: Record<string, unknown> | null): string {
  if (!data) return "No query data";
  const parts: string[] = [];
  const freeText = (data as any)?.free_text;
  const useCases = (data as any)?.use_cases;
  if (freeText && typeof freeText === "string") parts.push(freeText.slice(0, 80));
  if (Array.isArray(useCases) && useCases.length > 0) parts.push(useCases.join(", "));
  return parts.join(" | ") || "No query data";
}

function FeedbackCard({ item, index }: { item: PublicFeedbackEntry; index: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
      className="border p-4"
      style={{ borderColor: "rgba(23, 147, 209, 0.12)", backgroundColor: "rgba(23, 147, 209, 0.02)" }}
    >
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          {item.rating && (
            <div className="flex items-center gap-0.5 mb-2">
              {[1, 2, 3, 4, 5].map((star) => (
                <Star
                  key={star}
                  size={12}
                  fill={star <= item.rating! ? ARCH_BLUE : "none"}
                  stroke={star <= item.rating! ? ARCH_BLUE : "rgba(255,255,255,0.1)"}
                />
              ))}
            </div>
          )}
          <p className="text-xs font-mono-terminal" style={{ color: "#888" }}>
            {formatDate(item.created_at)}
          </p>
          <p className="mt-2 text-xs font-mono-terminal" style={{ color: "#ccc" }}>
            {requestSummary(item.request_data as any)}
          </p>
        </div>
      </div>

      {item.comment && (
        <div className="mt-3 pt-3 border-t" style={{ borderColor: "rgba(23, 147, 209, 0.08)" }}>
          <div className="flex items-start gap-1.5">
            <MessageSquare size={11} style={{ color: "#555", marginTop: 1 }} className="shrink-0" />
            <p className="text-xs font-mono-terminal leading-relaxed" style={{ color: "#aaa" }}>
              {item.comment}
            </p>
          </div>
        </div>
      )}
    </motion.div>
  );
}

export default function PublicFeedbackPage() {
  const navigate = useNavigate();
  const [items, setItems] = useState<PublicFeedbackEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    getPublicFeedback()
      .then((data) => {
        if (!cancelled) setItems(data.items || []);
      })
      .catch((err) => {
        if (!cancelled) setError(err instanceof Error ? err.message : "Failed to load feedback");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => { cancelled = true; };
  }, []);

  return (
    <div className="min-h-screen text-white selection:bg-[#1793D1]/30" style={{ backgroundColor: "#0a0a0f" }}>
      <div className="fixed inset-0 pointer-events-none">
        <div
          className="absolute top-[-20%] left-1/2 -translate-x-1/2 w-[800px] h-[600px] rounded-full blur-[120px]"
          style={{ backgroundColor: "rgba(23, 147, 209, 0.04)" }}
        />
      </div>

      <div className="relative z-10 flex flex-col min-h-screen">
        <nav
          className="flex items-center justify-between px-6 py-4 max-w-6xl mx-auto w-full border-b"
          style={{ borderColor: "rgba(23, 147, 209, 0.12)" }}
        >
          <div className="flex items-center gap-2.5">
            <div
              className="flex items-center justify-center w-7 h-7 cursor-pointer"
              onClick={() => navigate("/")}
            >
              <img src="/icons.png" alt="I Can Run Linux" className="w-7 h-7" />
            </div>
            <span
              className="text-xs font-medium tracking-tight font-mono-terminal cursor-pointer"
              style={{ color: "#e2e2e2" }}
              onClick={() => navigate("/")}
            >
              <span style={{ color: ARCH_BLUE }}>$</span> icanrunlinux
            </span>
          </div>
          <button
            onClick={() => navigate("/")}
            className="flex items-center gap-1.5 text-xs font-mono-terminal text-zinc-500 hover:text-[#1793D1] transition-colors"
          >
            <ArrowLeft size={12} />
            back home
          </button>
        </nav>

        <main className="flex-1 px-6">
          <div className="max-w-2xl mx-auto pt-8 pb-12">
            <div className="mb-6">
              <div className="flex items-center gap-2 mb-2">
                <MessageSquare size={16} style={{ color: ARCH_BLUE }} />
                <h1 className="text-lg font-medium text-white font-mono-terminal">
                  Community Feedback
                </h1>
              </div>
              <p className="text-xs font-mono-terminal" style={{ color: "#555" }}>
                Public feedback and ratings from users who tested their hardware compatibility.
              </p>
            </div>

            {loading ? (
              <div className="flex items-center justify-center py-20">
                <div className="h-6 w-6 border-2 border-white/10 border-t-[#1793D1] rounded-full animate-spin" />
              </div>
            ) : error ? (
              <div className="text-center py-20">
                <p className="text-xs font-mono-terminal text-red-400">[error] {error}</p>
              </div>
            ) : items.length === 0 ? (
              <div className="text-center py-20">
                <Search size={32} style={{ color: "#333" }} className="mx-auto mb-4" />
                <p className="text-xs font-mono-terminal" style={{ color: "#555" }}>
                  No feedback yet. Be the first to run a compatibility check!
                </p>
                <button
                  onClick={() => navigate("/")}
                  className="mt-4 text-xs font-mono-terminal text-[#1793D1] hover:underline"
                >
                  start a check
                </button>
              </div>
            ) : (
              <div className="space-y-3">
                {items.map((item, i) => (
                  <FeedbackCard key={i} item={item} index={i} />
                ))}
              </div>
            )}
          </div>
        </main>

        <footer className="border-t mt-auto" style={{ borderColor: "rgba(23, 147, 209, 0.08)" }}>
          <div className="max-w-6xl mx-auto px-6 py-4 flex flex-row items-center text-sm font-mono-terminal" style={{ color: "#444" }}>
            <div className="flex items-center gap-2">
              <img src="/icons.png" alt="I Can Run Linux" className="w-4 h-4" />
              <span>icanrunlinux</span>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
}
