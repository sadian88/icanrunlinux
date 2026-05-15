import { motion } from "framer-motion";
import { BarChart3, Gauge, Cpu, Layers, Sparkles, Database, Zap } from "lucide-react";
import type { RecommendResult } from "../types/distro";

interface Props {
  item: RecommendResult;
}

const DIFFICULTY_LABELS: Record<number, string> = {
  1: "Beginner",
  2: "Easy",
  3: "Intermediate",
  4: "Advanced",
  5: "Expert",
};

const SOURCE_META: Record<string, { label: string; icon: React.ReactNode; color: string }> = {
  database: {
    label: "DistroWatch",
    icon: <Database size={10} />,
    color: "text-zinc-400 border-zinc-700 bg-zinc-800/50",
  },
  ai_cache: {
    label: "AI Cache",
    icon: <Zap size={10} />,
    color: "text-amber-300 border-amber-500/30 bg-amber-500/10",
  },
  llm: {
    label: "AI Powered",
    icon: <Sparkles size={10} />,
    color: "text-emerald-300 border-emerald-500/30 bg-emerald-500/10",
  },
};

const cardVariants = {
  hidden: { opacity: 0, y: 12 },
  show: { opacity: 1, y: 0, transition: { duration: 0.35, ease: "easeOut" as const } },
};

export default function DistroCard({ item }: Props) {
  const { distro, similarity, source, ai_reason } = item;
  const meta = SOURCE_META[source] ?? SOURCE_META.database;

  return (
    <motion.div
      variants={cardVariants}
      className="group relative rounded-xl border border-white/10 bg-white/[0.03] p-5 hover:bg-white/[0.06] hover:border-white/20 transition-all duration-300 cursor-default"
    >
      {/* Subtle left accent line on hover */}
      <div className="absolute left-0 top-4 bottom-4 w-[2px] rounded-r-full bg-white/0 group-hover:bg-white/20 transition-colors duration-300" />

      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-3">
            <h3 className="text-base font-medium text-white truncate">
              {distro.name}
            </h3>
            {distro.origin && (
              <span className="text-xs text-zinc-600 hidden sm:inline-block">
                {distro.origin}
              </span>
            )}
          </div>

          {distro.description && (
            <p className="mt-2 text-sm text-zinc-400 line-clamp-2 leading-relaxed">
              {distro.description}
            </p>
          )}
        </div>

        <div className="shrink-0 flex flex-col items-end gap-1.5">
          <div className="flex items-center gap-1.5 rounded-full bg-white/10 px-2.5 py-1">
            <BarChart3 size={12} className="text-zinc-300" />
            <span className="text-xs font-medium text-white">
              {Math.round(similarity * 100)}%
            </span>
          </div>
          <span className="text-[10px] text-zinc-600 uppercase tracking-wider font-medium">
            match
          </span>
        </div>
      </div>

      {/* AI reason badge */}
      {ai_reason && (
        <div className="mt-3 rounded-lg border border-emerald-500/20 bg-emerald-500/5 px-3 py-2">
          <div className="flex items-start gap-2">
            <Sparkles size={14} className="text-emerald-400 mt-0.5 shrink-0" />
            <p className="text-xs text-emerald-200/80 leading-relaxed">
              {ai_reason}
            </p>
          </div>
        </div>
      )}

      {/* Tags */}
      <div className="mt-4 flex flex-wrap gap-2">
        {distro.recommended_for.slice(0, 4).map((uc) => (
          <span
            key={uc}
            className="inline-flex items-center rounded-full border border-white/10 bg-white/5 px-2.5 py-0.5 text-[11px] text-zinc-400"
          >
            {uc.replace(/_/g, " ")}
          </span>
        ))}
      </div>

      {/* Stats + Source */}
      <div className="mt-5 grid grid-cols-3 gap-4 pt-4 border-t border-white/5">
        <div className="flex items-center gap-2">
          <Gauge size={14} className="text-zinc-600" />
          <div>
            <span className="block text-xs text-zinc-300 font-medium">
              {DIFFICULTY_LABELS[distro.difficulty] ?? `Level ${distro.difficulty}`}
            </span>
            <span className="text-[10px] text-zinc-600 uppercase tracking-wider">
              Difficulty
            </span>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Cpu size={14} className="text-zinc-600" />
          <div>
            <span className="block text-xs text-zinc-300 font-medium">
              {distro.min_ram_gb ? `${distro.min_ram_gb} GB` : "—"}
            </span>
            <span className="text-[10px] text-zinc-600 uppercase tracking-wider">
              Min RAM
            </span>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Layers size={14} className="text-zinc-600" />
          <div>
            <span className="block text-xs text-zinc-300 font-medium">
              {distro.architectures.length}
            </span>
            <span className="text-[10px] text-zinc-600 uppercase tracking-wider">
              Architectures
            </span>
          </div>
        </div>
      </div>

      {/* Source badge */}
      <div className="mt-4 flex justify-end">
        <span
          className={`inline-flex items-center gap-1.5 rounded-full border px-2 py-0.5 text-[10px] font-medium uppercase tracking-wider ${meta.color}`}
        >
          {meta.icon}
          {meta.label}
        </span>
      </div>
    </motion.div>
  );
}
