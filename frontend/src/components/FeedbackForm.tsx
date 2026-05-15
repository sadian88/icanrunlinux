import { useState } from "react";
import { motion } from "framer-motion";
import { Star, Send, Check, AlertCircle } from "lucide-react";
import { submitFeedback } from "../services/api";

const ARCH_BLUE = "#1793D1";
const ARCH_BLUE_BORDER = "rgba(23, 147, 209, 0.25)";

interface Props {
  sessionToken: string;
}

export default function FeedbackForm({ sessionToken }: Props) {
  const [rating, setRating] = useState<number>(0);
  const [hoverRating, setHoverRating] = useState<number>(0);
  const [comment, setComment] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async () => {
    if (submitted || submitting) return;
    setSubmitting(true);
    setError(null);
    try {
      await submitFeedback({
        session_token: sessionToken,
        rating: rating > 0 ? rating : undefined,
        comment: comment.trim() || undefined,
      });
      setSubmitted(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to submit feedback");
    } finally {
      setSubmitting(false);
    }
  };

  if (submitted) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        className="mt-6 border px-4 py-3 flex items-center gap-2"
        style={{ borderColor: "rgba(23, 147, 209, 0.15)", backgroundColor: "rgba(23, 147, 209, 0.04)" }}
      >
        <Check size={14} style={{ color: ARCH_BLUE }} />
        <span className="text-xs font-mono-terminal" style={{ color: ARCH_BLUE }}>
          Feedback submitted. Thanks!
        </span>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3 }}
      className="mt-8 border p-4"
      style={{ borderColor: ARCH_BLUE_BORDER, backgroundColor: "var(--bg-surface)" }}
    >
      <div className="flex items-center gap-2 mb-3">
        <Star size={12} style={{ color: ARCH_BLUE }} />
        <span className="text-xs font-mono-terminal" style={{ color: "#888" }}>
          Rate this search
        </span>
      </div>

      <div className="flex items-center gap-1 mb-3">
        {[1, 2, 3, 4, 5].map((star) => (
          <button
            key={star}
            onClick={() => setRating(star)}
            onMouseEnter={() => setHoverRating(star)}
            onMouseLeave={() => setHoverRating(0)}
            className="transition-colors"
          >
            <Star
              size={18}
              fill={star <= (hoverRating || rating) ? ARCH_BLUE : "none"}
              stroke={star <= (hoverRating || rating) ? ARCH_BLUE : "rgba(255,255,255,0.15)"}
            />
          </button>
        ))}
        {rating > 0 && (
          <span className="text-xs font-mono-terminal ml-2" style={{ color: "#666" }}>
            {rating}/5
          </span>
        )}
      </div>

      <textarea
        value={comment}
        onChange={(e) => setComment(e.target.value)}
        rows={3}
        placeholder="Add a comment (optional)..."
        maxLength={2000}
        className="w-full border px-3 py-2 text-xs font-mono-terminal resize-none focus:outline-none transition-all mb-3"
        style={{
          borderColor: "rgba(23, 147, 209, 0.15)",
          backgroundColor: "rgba(23, 147, 209, 0.03)",
          color: "#ccc",
        }}
        onFocus={(e) => {
          e.currentTarget.style.borderColor = ARCH_BLUE_BORDER;
          e.currentTarget.style.backgroundColor = "rgba(23, 147, 209, 0.06)";
        }}
        onBlur={(e) => {
          e.currentTarget.style.borderColor = "rgba(23, 147, 209, 0.15)";
          e.currentTarget.style.backgroundColor = "rgba(23, 147, 209, 0.03)";
        }}
      />

      {error && (
        <div className="flex items-center gap-1.5 mb-3">
          <AlertCircle size={12} className="text-red-400" />
          <span className="text-xs font-mono-terminal text-red-400">{error}</span>
        </div>
      )}

      <button
        onClick={handleSubmit}
        disabled={submitting}
        className="flex items-center gap-2 border px-4 py-2 text-xs font-mono-terminal transition-all hover:bg-[#1793D1]/10 disabled:opacity-50 disabled:cursor-not-allowed"
        style={{ borderColor: ARCH_BLUE_BORDER, color: ARCH_BLUE }}
      >
        {submitting ? (
          <>
            <span className="h-3 w-3 border-2 border-[#1793D1]/30 border-t-[#1793D1] rounded-full animate-spin" />
            submitting...
          </>
        ) : (
          <>
            <Send size={12} />
            submit feedback
          </>
        )}
      </button>
    </motion.div>
  );
}
