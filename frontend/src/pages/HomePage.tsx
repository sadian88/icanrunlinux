import { useCallback, useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { History } from "lucide-react";
import type { RecommendRequest } from "../types/distro";
import SearchWizard from "../components/SearchWizard";
import PixelTypewriter from "../components/PixelTypewriter";
import SearchHistory from "../components/SearchHistory";

const ARCH_BLUE = "#1793D1";

interface Props {
  onSubmit: (req: RecommendRequest) => void;
}

export default function HomePage({ onSubmit }: Props) {
  const [showHistory, setShowHistory] = useState(false);
  const navigate = useNavigate();

  const handleSearch = useCallback(
    (req: RecommendRequest) => {
      onSubmit(req);
    },
    [onSubmit],
  );

  return (
    <div className="min-h-screen text-white selection:bg-[#1793D1]/30" style={{ backgroundColor: "#0a0a0f" }}>
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
            <div
              className="flex items-center justify-center w-7 h-7"
            >
              <img src="/icons.png" alt="I Can Run Linux" className="w-7 h-7" />
            </div>
            <span className="text-xs font-medium tracking-tight font-mono-terminal" style={{ color: "#e2e2e2" }}>
              <span style={{ color: ARCH_BLUE }}>$</span> icanrunlinux
            </span>
          </div>
          <div className="hidden sm:flex items-center gap-6 text-xs font-mono-terminal" style={{ color: "#555" }}>
            <button
              onClick={() => navigate("/feedback")}
              className="hover:text-[#1793D1] transition-colors cursor-pointer"
            >
              users feedback
            </button>
            <button
              onClick={() => setShowHistory(true)}
              className="flex items-center gap-1.5 hover:text-[#1793D1] transition-colors cursor-pointer"
            >
              <History size={12} />
              my history
            </button>
          </div>
        </nav>

        {/* Hero */}
        <main className="flex-1 px-6">
          <div className="max-w-4xl mx-auto text-center pt-6 sm:pt-10 pb-6">
            <div className="flex justify-center mb-4">
              <PixelTypewriter />
            </div>

            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, ease: "easeOut", delay: 0.4 }}
              className="mt-3 text-sm sm:text-base max-w-2xl mx-auto leading-relaxed font-mono-terminal"
              style={{ color: "#666" }}
            >
              Describe your hardware. We match you with the best Linux distro
              using vector similarity search and AI reasoning.
            </motion.p>
          </div>

          {/* Wizard */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.5 }}
            className="max-w-2xl mx-auto pb-8"
          >
            <SearchWizard loading={false} onSubmit={handleSearch} />
          </motion.div>
        </main>

        {/* Footer */}
        <footer className="border-t mt-auto" style={{ borderColor: "rgba(23, 147, 209, 0.08)" }}>
          <div className="max-w-6xl mx-auto px-6 py-4 flex flex-row items-center text-[10px] font-mono-terminal" style={{ color: "#444" }}>
            <div className="flex items-center gap-2">
              <img src="/icons.png" alt="I Can Run Linux" className="w-4 h-4" />
              <span>icanrunlinux</span>
            </div>
          </div>
        </footer>
      </div>

      <SearchHistory open={showHistory} onClose={() => setShowHistory(false)} />
    </div>
  );
}
