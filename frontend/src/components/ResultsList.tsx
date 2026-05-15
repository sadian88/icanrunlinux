import { motion } from "framer-motion";
import type { RecommendResult } from "../types/distro";
import DistroCard from "./DistroCard";

interface Props {
  results: RecommendResult[];
  loading: boolean;
}

const containerVariants = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.08,
    },
  },
};

export default function ResultsList({ results, loading }: Props) {
  if (loading) {
    return (
      <section className="mt-16 max-w-2xl mx-auto">
        <div className="flex items-center justify-center py-20">
          <div className="flex flex-col items-center gap-4">
            <div className="h-8 w-8 border-2 border-white/10 border-t-white rounded-full animate-spin" />
            <p className="text-sm text-zinc-500">Matching distros...</p>
          </div>
        </div>
      </section>
    );
  }

  if (results.length === 0) {
    return (
      <section className="mt-16 max-w-2xl mx-auto text-center">
        <p className="text-zinc-500 text-sm">
          No distributions matched your criteria. Try adjusting your hardware
          description or use cases.
        </p>
      </section>
    );
  }

  return (
    <section className="mt-16 max-w-2xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-medium text-white">
          Recommended distributions
        </h2>
        <span className="text-xs text-zinc-500 uppercase tracking-wider font-medium">
          {results.length} results
        </span>
      </div>

      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="show"
        className="space-y-3"
      >
        {results.map((item) => (
          <DistroCard key={item.distro.id} item={item} />
        ))}
      </motion.div>
    </section>
  );
}
