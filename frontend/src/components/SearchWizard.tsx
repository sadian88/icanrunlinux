import { useCallback, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ArrowRight, ArrowLeft, Cpu, Search, Sparkles } from "lucide-react";
import type { RecommendRequest } from "../types/distro";

const ARCH_BLUE = "#1793D1";
const ARCH_BLUE_BORDER = "rgba(23, 147, 209, 0.25)";

const USE_CASES = [
  { id: "desktop", label: "Desktop / general use" },
  { id: "servers", label: "Servers / hosting" },
  { id: "development", label: "Development / programming" },
  { id: "gaming", label: "Gaming" },
  { id: "customization", label: "Customization" },
  { id: "modern_ui", label: "Modern UI / GNOME or KDE" },
  { id: "low_resources", label: "Low resources / old hardware" },
];

const TOTAL_STEPS = 3;

interface Props {
  loading: boolean;
  onSubmit: (req: RecommendRequest) => void;
}

const stepVariants = {
  initial: (direction: number) => ({
    x: direction > 0 ? 40 : -40,
    opacity: 0,
  }),
  animate: {
    x: 0,
    opacity: 1,
    transition: { duration: 0.35, ease: "easeOut" as const },
  },
  exit: (direction: number) => ({
    x: direction > 0 ? -40 : 40,
    opacity: 0,
    transition: { duration: 0.25, ease: "easeIn" as const },
  }),
};

export default function SearchWizard({ loading, onSubmit }: Props) {
  const [step, setStep] = useState(1);
  const [direction, setDirection] = useState(1);
  const [hardwareText, setHardwareText] = useState("");
  const [selectedUses, setSelectedUses] = useState<string[]>([]);
  const [needsText, setNeedsText] = useState("");

  const toggleUseCase = (id: string) => {
    setSelectedUses((prev) =>
      prev.includes(id) ? prev.filter((u) => u !== id) : [...prev, id],
    );
  };

  const handleNext = () => {
    setDirection(1);
    setStep((s) => Math.min(s + 1, TOTAL_STEPS));
  };

  const handleBack = () => {
    setDirection(-1);
    setStep((s) => Math.max(s - 1, 1));
  };

  const handleSubmit = useCallback(() => {
    const parts = [hardwareText, needsText].filter(Boolean);
    const freeText = parts.join(" | ");

    const req: RecommendRequest = {
      free_text: freeText || undefined,
      use_cases: selectedUses.length > 0 ? selectedUses : undefined,
      limit: 10,
    };
    onSubmit(req);
  }, [hardwareText, needsText, selectedUses, onSubmit]);

  const progressPercent = (step / TOTAL_STEPS) * 100;

  return (
    <div className="w-full">
      {/* Terminal prompt header */}
      <div className="mb-4 flex items-center justify-between text-[10px] font-mono-terminal" style={{ color: "#444" }}>
        <span>
          <span style={{ color: ARCH_BLUE }}>$</span> ./wizard.sh
        </span>
        <span style={{ color: "#333" }}>
          {step}/{TOTAL_STEPS}
        </span>
      </div>

      <div
        className="relative overflow-hidden border"
        style={{
          borderColor: ARCH_BLUE_BORDER,
          backgroundColor: "rgba(17, 17, 24, 0.6)",
        }}
      >
        {/* Top progress line */}
        <div className="h-[1px] w-full" style={{ backgroundColor: "rgba(23, 147, 209, 0.08)" }}>
          <motion.div
            className="h-full"
            style={{ backgroundColor: ARCH_BLUE }}
            initial={{ width: 0 }}
            animate={{ width: `${progressPercent}%` }}
            transition={{ duration: 0.4, ease: "easeInOut" }}
          />
        </div>

        <div className="p-5 sm:p-6 min-h-[320px]">
          <AnimatePresence mode="wait" custom={direction}>
            {step === 1 && (
              <motion.div
                key="step1"
                custom={direction}
                variants={stepVariants}
                initial="initial"
                animate="animate"
                exit="exit"
                className="space-y-5"
              >
                <div className="space-y-2">
                  <div className="flex items-center gap-2" style={{ color: "#888" }}>
                    <Cpu size={14} style={{ color: ARCH_BLUE }} />
                    <h2 className="text-sm font-medium font-mono-terminal">Your Hardware</h2>
                  </div>
                  <p className="text-xs font-mono-terminal" style={{ color: "#444" }}>
                    Describe your PC specs — RAM, CPU, storage, GPU.
                  </p>
                </div>

                <div className="space-y-1.5">
                  <div className="text-[10px] font-mono-terminal" style={{ color: "#333" }}>
                    <span style={{ color: ARCH_BLUE }}>$</span> cat hardware.conf
                  </div>
                  <textarea
                    value={hardwareText}
                    onChange={(e) => setHardwareText(e.target.value)}
                    rows={4}
                    placeholder='e.g. "Old laptop with 4GB RAM, Intel Core i3, 120GB SSD"'
                    className="w-full border px-3 py-2.5 text-xs font-mono-terminal resize-none focus:outline-none transition-all"
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
                </div>

                <div className="flex justify-end">
                  <button
                    onClick={handleNext}
                    className="group flex items-center gap-2 border px-4 py-2 text-xs font-mono-terminal transition-all hover:bg-[#1793D1]/10"
                    style={{
                      borderColor: ARCH_BLUE_BORDER,
                      color: ARCH_BLUE,
                    }}
                  >
                    next
                    <ArrowRight size={12} className="transition-transform group-hover:translate-x-0.5" />
                  </button>
                </div>
              </motion.div>
            )}

            {step === 2 && (
              <motion.div
                key="step2"
                custom={direction}
                variants={stepVariants}
                initial="initial"
                animate="animate"
                exit="exit"
                className="space-y-5"
              >
                <div className="space-y-2">
                  <div className="flex items-center gap-2" style={{ color: "#888" }}>
                    <Sparkles size={14} style={{ color: ARCH_BLUE }} />
                    <h2 className="text-sm font-medium font-mono-terminal">Use Cases</h2>
                  </div>
                  <p className="text-xs font-mono-terminal" style={{ color: "#444" }}>
                    Select all the ways you plan to use your Linux system.
                  </p>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {USE_CASES.map((uc) => {
                    const selected = selectedUses.includes(uc.id);
                    return (
                      <button
                        key={uc.id}
                        onClick={() => toggleUseCase(uc.id)}
                        className="flex items-center justify-between border px-3 py-2.5 text-xs font-mono-terminal transition-all duration-200"
                        style={{
                          borderColor: selected ? ARCH_BLUE_BORDER : "rgba(23, 147, 209, 0.1)",
                          backgroundColor: selected ? "rgba(23, 147, 209, 0.08)" : "transparent",
                          color: selected ? "#ccc" : "#555",
                        }}
                        onMouseEnter={(e) => {
                          if (!selected) {
                            e.currentTarget.style.borderColor = ARCH_BLUE_BORDER;
                            e.currentTarget.style.color = "#999";
                          }
                        }}
                        onMouseLeave={(e) => {
                          if (!selected) {
                            e.currentTarget.style.borderColor = "rgba(23, 147, 209, 0.1)";
                            e.currentTarget.style.color = "#555";
                          }
                        }}
                      >
                        <span>{uc.label}</span>
                        {selected && (
                          <motion.div
                            initial={{ scale: 0 }}
                            animate={{ scale: 1 }}
                            className="h-3 w-3 flex items-center justify-center"
                            style={{ backgroundColor: ARCH_BLUE }}
                          >
                            <div className="h-1 w-1 bg-black" />
                          </motion.div>
                        )}
                      </button>
                    );
                  })}
                </div>

                <div className="flex justify-between">
                  <button
                    onClick={handleBack}
                    className="flex items-center gap-2 border px-4 py-2 text-xs font-mono-terminal transition-all hover:bg-white/5"
                    style={{
                      borderColor: "rgba(255,255,255,0.08)",
                      color: "#666",
                    }}
                  >
                    <ArrowLeft size={12} />
                    back
                  </button>
                  <button
                    onClick={handleNext}
                    className="group flex items-center gap-2 border px-4 py-2 text-xs font-mono-terminal transition-all hover:bg-[#1793D1]/10"
                    style={{
                      borderColor: ARCH_BLUE_BORDER,
                      color: ARCH_BLUE,
                    }}
                  >
                    next
                    <ArrowRight size={12} className="transition-transform group-hover:translate-x-0.5" />
                  </button>
                </div>
              </motion.div>
            )}

            {step === 3 && (
              <motion.div
                key="step3"
                custom={direction}
                variants={stepVariants}
                initial="initial"
                animate="animate"
                exit="exit"
                className="space-y-5"
              >
                <div className="space-y-2">
                  <div className="flex items-center gap-2" style={{ color: "#888" }}>
                    <Search size={14} style={{ color: ARCH_BLUE }} />
                    <h2 className="text-sm font-medium font-mono-terminal">Anything Else?</h2>
                  </div>
                  <p className="text-xs font-mono-terminal" style={{ color: "#444" }}>
                    Add any extra requirements — desktop env, privacy, rolling release, etc.
                  </p>
                </div>

                <div className="space-y-1.5">
                  <div className="text-[10px] font-mono-terminal" style={{ color: "#333" }}>
                    <span style={{ color: ARCH_BLUE }}>$</span> cat requirements.conf
                  </div>
                  <textarea
                    value={needsText}
                    onChange={(e) => setNeedsText(e.target.value)}
                    rows={4}
                    placeholder='e.g. "beginner-friendly, works with NVIDIA GPUs, good for web development"'
                    className="w-full border px-3 py-2.5 text-xs font-mono-terminal resize-none focus:outline-none transition-all"
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
                </div>

                <div className="flex justify-between">
                  <button
                    onClick={handleBack}
                    className="flex items-center gap-2 border px-4 py-2 text-xs font-mono-terminal transition-all hover:bg-white/5"
                    style={{
                      borderColor: "rgba(255,255,255,0.08)",
                      color: "#666",
                    }}
                  >
                    <ArrowLeft size={12} />
                    back
                  </button>
                  <button
                    onClick={handleSubmit}
                    disabled={loading}
                    className="group flex items-center gap-2 border px-5 py-2 text-xs font-mono-terminal transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                    style={{
                      borderColor: ARCH_BLUE_BORDER,
                      backgroundColor: "rgba(23, 147, 209, 0.1)",
                      color: ARCH_BLUE,
                    }}
                  >
                    {loading ? (
                      <>
                        <span className="h-3 w-3 border-2 border-[#1793D1]/30 border-t-[#1793D1] rounded-full animate-spin" />
                        analyzing...
                      </>
                    ) : (
                      <>
                        find_distros
                        <ArrowRight size={12} className="transition-transform group-hover:translate-x-0.5" />
                      </>
                    )}
                  </button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}
