import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, Star, Search, Clock, MessageSquare } from "lucide-react";
import type { RecommendRequest, SearchHistoryEntry } from "../types/distro";
import { getHistory } from "../services/api";

const ARCH_BLUE = "#1793D1";
const ARCH_BLUE_BORDER = "rgba(23, 147, 209, 0.25)";

interface Props {
  open: boolean;
  onClose: () => void;
}

function formatDate(d: string | null): string {
  if (!d) return "—";
  return new Date(d).toLocaleString();
}

function requestSummary(data: RecommendRequest | null): string {
  if (!data) return "No query data";
  const parts: string[] = [];
  const freeText = data.free_text;
  const useCases = data.use_cases;
  if (freeText && typeof freeText === "string") parts.push(freeText.slice(0, 80));
  if (Array.isArray(useCases) && useCases.length > 0) parts.push(useCases.join(", "));
  return parts.join(" | ") || "No query data";
}

export default function SearchHistory({ open, onClose }: Props) {
  const [sessions, setSessions] = useState<SearchHistoryEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!open) return;
    let cancelled = false;
    setLoading(true);
    setError(null);
    getHistory()
      .then((data) => {
        if (!cancelled) setSessions(data.sessions || []);
      })
      .catch((err) => {
        if (!cancelled) setError(err instanceof Error ? err.message : "Failed to load history");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => { cancelled = true; };
  }, [open]);

  return (
    <AnimatePresence>
      {open && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-50 flex items-start justify-center pt-20 px-4"
          style={{ backgroundColor: "rgba(0,0,0,0.7)" }}
          onClick={onClose}
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 10 }}
            transition={{ duration: 0.2 }}
            className="w-full max-w-xl max-h-[80vh] overflow-hidden border flex flex-col"
            style={{ borderColor: ARCH_BLUE_BORDER, backgroundColor: "var(--bg-base)" }}
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div
              className="flex items-center justify-between px-4 py-3 border-b shrink-0"
              style={{ borderColor: "rgba(23, 147, 209, 0.1)" }}
            >
              <div className="flex items-center gap-2">
                <Search size={13} style={{ color: ARCH_BLUE }} />
                <span className="text-xs font-mono-terminal" style={{ color: "#ccc" }}>
                  my search history
                </span>
              </div>
              <button
                onClick={onClose}
                className="hover:bg-white/10 p-1 transition-colors"
              >
                <X size={14} style={{ color: "#666" }} />
              </button>
            </div>

            {/* Content */}
            <div className="overflow-y-auto flex-1 p-4">
              {loading ? (
                <div className="flex items-center justify-center py-12">
                  <div className="h-5 w-5 border-2 border-white/10 border-t-[#1793D1] rounded-full animate-spin" />
                </div>
              ) : error ? (
                <div className="text-center py-12">
                  <p className="text-xs font-mono-terminal text-red-400">{error}</p>
                </div>
              ) : sessions.length === 0 ? (
                <div className="text-center py-12">
                  <Search size={24} style={{ color: "#333" }} className="mx-auto mb-3" />
                  <p className="text-xs font-mono-terminal" style={{ color: "#555" }}>
                    No searches yet.
                  </p>
                </div>
              ) : (
                <div className="space-y-3">
                  {sessions.map((s) => (
                    <div
                      key={s.session_token}
                      className="border p-3"
                      style={{ borderColor: "rgba(23, 147, 209, 0.1)", backgroundColor: "rgba(23, 147, 209, 0.02)" }}
                    >
                      <div className="flex items-center gap-2 mb-2">
                        <Clock size={10} style={{ color: "#555" }} />
                        <span className="text-xs font-mono-terminal" style={{ color: "#666" }}>
                          {formatDate(s.created_at)}
                        </span>
                        {s.feedback?.rating && (
                          <span className="flex items-center gap-0.5 ml-auto">
                            <Star size={10} fill={ARCH_BLUE} stroke={ARCH_BLUE} />
                            <span className="text-xs font-mono-terminal" style={{ color: ARCH_BLUE }}>
                              {s.feedback.rating}
                            </span>
                          </span>
                        )}
                      </div>
                      <p className="text-xs font-mono-terminal mb-2" style={{ color: "#999" }}>
                        {requestSummary(s.request_data)}
                      </p>
                      {s.feedback?.comment && (
                        <div className="flex items-start gap-1.5 mt-2 pt-2 border-t" style={{ borderColor: "rgba(255,255,255,0.05)" }}>
                          <MessageSquare size={10} style={{ color: "#555", marginTop: 1 }} />
                          <p className="text-xs font-mono-terminal" style={{ color: "#888" }}>
                            {s.feedback.comment.slice(0, 200)}
                            {s.feedback.comment.length > 200 ? "..." : ""}
                          </p>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
