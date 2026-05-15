import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { ArrowLeft, ChevronDown, ChevronUp } from "lucide-react";
import type { RecommendRequest, RecommendResult } from "../types/distro";
import { recommend } from "../services/api";
import FeedbackForm from "../components/FeedbackForm";

const ARCH_BLUE = "#1793D1";

function PixelLoading() {
  const text = "ANALYZING...";

  return (
    <div className="flex flex-col items-center justify-center py-20 gap-5">
      <div
        className="text-xs tracking-[0.2em] text-[#1793D1]"
        style={{ fontFamily: "'Press Start 2P', monospace" }}
      >
        {text.split("").map((char, i) => (
          <motion.span
            key={i}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{
              delay: i * 0.06,
              duration: 0.04,
              repeat: Infinity,
              repeatType: "reverse",
              repeatDelay: 0.4,
            }}
          >
            {char}
          </motion.span>
        ))}
      </div>
      <div className="flex gap-1">
        {[0, 1, 2, 3, 4].map((i) => (
          <motion.div
            key={i}
            animate={{ opacity: [0.2, 1, 0.2] }}
            transition={{ duration: 1.2, repeat: Infinity, delay: i * 0.15 }}
            className="w-3 h-1 bg-[#1793D1] rounded-none"
          />
        ))}
      </div>
      <div className="text-sm text-[#1793D1]/50 font-mono-terminal mt-1">
        $ pacman -Syu matching-engine
      </div>
    </div>
  );
}

function DistroResult({ item, index }: { item: RecommendResult; index: number }) {
  const hasTechnical = item.distro.package_manager || item.distro.init_system || item.distro.release_model;
  const [showTech, setShowTech] = useState(false);

  return (
    <motion.div
      initial={{ opacity: 0, x: -8 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.06 }}
      className="relative border px-3.5 py-3 transition-colors"
      style={{ borderColor: "rgba(23, 147, 209, 0.15)", backgroundColor: "var(--bg-surface)" }}
    >
      <div className="absolute -left-px top-0 bottom-0 w-[2px]" style={{ backgroundColor: ARCH_BLUE }} />

      <div className="flex items-start gap-3">
        <div className="flex flex-col items-center gap-0.5 pt-0.5 min-w-[24px]">
          <span className="text-lg leading-none font-mono-terminal" style={{ color: ARCH_BLUE }}>
            ●
          </span>
          <span className="text-xs text-[#1793D1]/60 font-mono-terminal font-bold">
            {index + 1}
          </span>
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between gap-2">
            <h4 className="text-base font-medium text-zinc-100 font-mono-terminal truncate">
              {item.distro.name}
            </h4>
            <div className="flex items-center gap-1.5 shrink-0">
              <span className="text-sm text-zinc-600 font-mono-terminal">match:</span>
              <span className="text-xs font-bold font-mono-terminal" style={{ color: ARCH_BLUE }}>
                {Math.round(item.similarity * 100)}%
              </span>
            </div>
          </div>

          <p className="mt-1 text-xs text-zinc-500 leading-relaxed line-clamp-2 font-mono-terminal">
            {item.distro.description || "No description available."}
          </p>

          {/* Technical badges */}
          {hasTechnical && (
            <div className="mt-2 flex flex-wrap gap-1.5">
              {item.distro.package_manager && (
                <span
                  className="inline-flex items-center text-xs px-2 py-0.5 font-mono-terminal uppercase tracking-wider"
                  style={{
                    border: "1px solid rgba(23,147,209,0.2)",
                    backgroundColor: "rgba(23,147,209,0.06)",
                    color: "#1793D1",
                  }}
                >
                  {item.distro.package_manager}
                </span>
              )}
              {item.distro.init_system && (
                <span
                  className="inline-flex items-center text-xs px-2 py-0.5 font-mono-terminal uppercase tracking-wider"
                  style={{
                    border: "1px solid rgba(23,147,209,0.15)",
                    backgroundColor: "rgba(23,147,209,0.04)",
                    color: "#888",
                  }}
                >
                  {item.distro.init_system}
                </span>
              )}
              {item.distro.release_model && (
                <span
                  className="inline-flex items-center text-xs px-2 py-0.5 font-mono-terminal uppercase tracking-wider"
                  style={{
                    border: "1px solid rgba(23,147,209,0.15)",
                    backgroundColor: "rgba(23,147,209,0.04)",
                    color: "#888",
                  }}
                >
                  {item.distro.release_model}
                </span>
              )}
            </div>
          )}

          {/* Benchmarks */}
          {item.distro.benchmarks && item.distro.benchmarks.length > 0 && (
            <div className="mt-2 flex flex-wrap gap-1.5">
              {item.distro.benchmarks.slice(0, 4).map((bm, bi) => (
                <span
                  key={bi}
                  className="inline-flex items-center gap-1 text-xs px-2 py-0.5 font-mono-terminal"
                  style={{
                    border: "1px solid rgba(23,147,209,0.12)",
                    backgroundColor: "rgba(23,147,209,0.03)",
                    color: "#888",
                  }}
                >
                  {bm.test_name.length > 20 ? bm.test_name.slice(0, 18) + ".." : bm.test_name}: {bm.score}{bm.unit}
                </span>
              ))}
            </div>
          )}

          {/* Package stats */}
          {item.distro.package_stats && (
            <div className="mt-2 flex items-center gap-2 text-sm font-mono-terminal text-zinc-600">
              <span>pkgs:{item.distro.package_stats.total_packages}</span>
              {item.distro.package_stats.outdated_packages > 0 && (
                <>
                  <span className="text-zinc-700">|</span>
                  <span style={{ color: item.distro.package_stats.outdated_packages > 100 ? "#d97706" : "#666" }}>
                    outdated:{item.distro.package_stats.outdated_packages}
                  </span>
                </>
              )}
              {item.distro.package_stats.vulnerable_packages > 0 && (
                <>
                  <span className="text-zinc-700">|</span>
                  <span style={{ color: item.distro.package_stats.vulnerable_packages > 5 ? "#dc2626" : "#666" }}>
                    vuln:{item.distro.package_stats.vulnerable_packages}
                  </span>
                </>
              )}
              <span className="text-zinc-700">|</span>
              <span>newest:{item.distro.package_stats.newest_packages}</span>
            </div>
          )}

          {item.ai_reason && (
            <div
              className="mt-2 border px-2.5 py-1.5"
              style={{ borderColor: "rgba(23, 147, 209, 0.15)", backgroundColor: "rgba(23, 147, 209, 0.04)" }}
            >
              <div className="flex items-start gap-1.5">
                <span className="text-sm text-[#1793D1]/70 font-mono-terminal shrink-0 mt-0.5">#</span>
                <p className="text-sm text-[#1793D1]/70 leading-snug font-mono-terminal">{item.ai_reason}</p>
          </div>
        </div>
          )}

          {/* Technical notes (expandable) */}
          {item.distro.technical_notes && (
            <>
              <button
                onClick={() => setShowTech((v) => !v)}
                className="mt-1.5 flex items-center gap-1 text-xs text-zinc-600 hover:text-[#1793D1] font-mono-terminal transition-colors"
              >
                {showTech ? <ChevronUp size={9} /> : <ChevronDown size={9} />}
                {showTech ? "hide technical notes" : "technical notes"}
              </button>
              {showTech && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  className="mt-1.5 border-l-2 pl-2.5 py-1"
                  style={{ borderColor: "rgba(23,147,209,0.2)" }}
                >
                  <p className="text-sm text-zinc-500 leading-relaxed font-mono-terminal">
                    {item.distro.technical_notes}
                  </p>
                </motion.div>
              )}
            </>
          )}

          <div className="mt-2 flex items-center gap-3 text-sm font-mono-terminal">
            <span className="text-zinc-600">ram:{item.distro.min_ram_gb || "—"}</span>
            <span className="text-zinc-700">|</span>
            <span className="text-zinc-600">
              diff:{["beginner","easy","intermediate","advanced","expert"][(item.distro.difficulty || 3) - 1] || "mid"}
            </span>
            <span className="text-zinc-700">|</span>
            <span
              className={`uppercase ${
                item.source === "llm" ? "text-[#1793D1]" : item.source === "ai_cache" ? "text-cyan-400/70" : "text-zinc-700"
              }`}
            >
              src:{item.source === "llm" ? "ai" : item.source === "ai_cache" ? "cache" : "db"}
            </span>
          </div>
        </div>
      </div>
    </motion.div>
  );
}

export default function ResultsPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const request: RecommendRequest | undefined = (location.state as any)?.request;

  const [results, setResults] = useState<RecommendResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showAll, setShowAll] = useState(false);
  const [sessionToken, setSessionToken] = useState<string | null>(null);

  useEffect(() => {
    if (!request) {
      navigate("/", { replace: true });
      return;
    }

    let cancelled = false;

    const fetchResults = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await recommend(request);
        if (!cancelled) {
          setResults(data.results);
          setSessionToken(data.session_token);
        }
      } catch (err) {
        if (!cancelled) setError(err instanceof Error ? err.message : "Something went wrong");
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    fetchResults();
    return () => { cancelled = true; };
  }, [request, navigate]);

  const displayed = showAll ? results : results.slice(0, 3);

  return (
    <div className="min-h-screen text-white selection:bg-[#1793D1]/30" style={{ backgroundColor: "var(--bg-base)" }}>
      <div className="fixed inset-0 pointer-events-none">
        <div
          className="absolute top-[-20%] left-1/2 -translate-x-1/2 w-[800px] h-[600px] rounded-full blur-[120px]"
          style={{ backgroundColor: "rgba(23, 147, 209, 0.04)" }}
        />
      </div>

      <div className="relative z-10 flex flex-col min-h-screen">
        {/* Navbar */}
        <nav
          className="flex items-center justify-between px-6 py-4 max-w-6xl mx-auto w-full border-b"
          style={{ borderColor: "rgba(23, 147, 209, 0.12)" }}
        >
          <div className="flex items-center gap-2.5">
            <div className="flex items-center justify-center w-7 h-7">
              <img src="/icons.png" alt="I Can Run Linux" className="w-7 h-7" />
            </div>
            <span className="text-xs font-medium tracking-tight font-mono-terminal" style={{ color: "#e2e2e2" }}>
              <span style={{ color: ARCH_BLUE }}>$</span> icanrunlinux
            </span>
          </div>
          <button
            onClick={() => navigate("/")}
            className="flex items-center gap-1.5 text-sm font-mono-terminal text-zinc-500 hover:text-[#1793D1] transition-colors"
          >
            <ArrowLeft size={10} />
            new search
          </button>
          <div className="hidden sm:flex items-center gap-4 text-sm font-mono-terminal">
            <button
              onClick={() => navigate("/feedback")}
              className="text-zinc-500 hover:text-[#1793D1] transition-colors"
            >
              feedback
            </button>
          </div>
        </nav>

        <main className="flex-1 px-6">
          <div className="max-w-2xl mx-auto pt-6 pb-8">
            {/* Header */}
            <div className="mb-6">
              <div className="font-mono-terminal text-sm text-[#1793D1]/60 mb-2">
                <span className="text-[#1793D1]">$</span> neofetch --distro_recommendation
              </div>

              {request?.free_text && (
                <div className="text-sm text-zinc-600 font-mono-terminal truncate max-w-full">
                  query: {request.free_text}
                </div>
              )}
            </div>

            {loading ? (
              <PixelLoading />
            ) : error ? (
              <div className="text-center py-12">
                <p className="text-sm text-red-400 font-mono-terminal">[error] {error}</p>
                <button
                  onClick={() => navigate("/")}
                  className="mt-4 text-sm text-[#1793D1] hover:underline font-mono-terminal"
                >
                  back to search
                </button>
              </div>
            ) : results.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-sm text-zinc-500 font-mono-terminal">No matching distributions found.</p>
                <button
                  onClick={() => navigate("/")}
                  className="mt-4 text-sm text-[#1793D1] hover:underline font-mono-terminal"
                >
                  try a different search
                </button>
              </div>
            ) : (
              <>
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <h2 className="text-sm font-medium font-mono-terminal">Recommendations</h2>
                    <span className="text-sm text-zinc-600 font-mono-terminal">({results.length})</span>
                  </div>
                  {!showAll && results.length > 3 && (
                    <span className="text-sm text-zinc-600 font-mono-terminal">
                      top 3 of {results.length}
                    </span>
                  )}
                </div>

                <div className="space-y-2">
                  <AnimatePresence>
                    {displayed.map((item, i) => (
                      <DistroResult key={item.distro.id} item={item} index={i} />
                    ))}
                  </AnimatePresence>
                </div>

                {/* Show more / less toggle */}
                {results.length > 3 && (
                  <button
                    onClick={() => setShowAll((v) => !v)}
                    className="w-full flex items-center justify-center gap-2 mt-3 py-3 border text-sm font-mono-terminal transition-colors hover:bg-[#1793D1]/5"
                    style={{ borderColor: "rgba(23, 147, 209, 0.15)", backgroundColor: "var(--bg-surface)", color: "#666" }}
                  >
                    {showAll ? (
                      <>
                        <ChevronUp size={10} />
                        show less
                      </>
                    ) : (
                      <>
                        <ChevronDown size={10} />
                        view all {results.length} results
                      </>
                    )}
                  </button>
                )}

                {sessionToken && !loading && results.length > 0 && (
                  <FeedbackForm sessionToken={sessionToken} />
                )}

                {/* Bottom prompt */}
                <div className="font-mono-terminal text-sm text-[#1793D1]/50 pt-4">
                  <span className="text-[#1793D1]">$</span> <span className="animate-pulse">_</span>
                </div>
              </>
            )}
          </div>
        </main>

        {/* Footer */}
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
