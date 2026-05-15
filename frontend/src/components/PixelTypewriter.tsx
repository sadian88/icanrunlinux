import { useState, useEffect } from "react";
import { motion } from "framer-motion";

const LINE1 = "Find the perfect";
const LINE2 = "Linux distribution.";

const containerVariants = {
  hidden: {},
  visible: {
    transition: {
      staggerChildren: 0.04,
    },
  },
};

const letterVariants = {
  hidden: { opacity: 0, y: 10, scale: 0.8 },
  visible: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: { duration: 0.1, ease: "easeOut" as const },
  },
};

export default function PixelTypewriter() {
  const [showCursor, setShowCursor] = useState(true);
  const [glitch, setGlitch] = useState(false);

  useEffect(() => {
    const interval = setInterval(() => {
      setShowCursor((prev) => !prev);
    }, 530);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const interval = setInterval(() => {
      setGlitch(true);
      setTimeout(() => setGlitch(false), 150);
    }, 4000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="relative inline-block">
      <div
        className={`absolute inset-0 blur-[40px] transition-opacity duration-150 ${
          glitch ? "bg-[#1793D1]/10 opacity-100" : "bg-[#1793D1]/5 opacity-50"
        }`}
      />

      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="relative z-10 text-xl sm:text-3xl md:text-4xl lg:text-5xl leading-relaxed sm:leading-relaxed tracking-tight"
        style={{ fontFamily: "'Press Start 2P', monospace" }}
      >
        <div className="block mb-2 sm:mb-4">
          {LINE1.split("").map((char, i) => (
            <motion.span
              key={`l1-${i}`}
              variants={letterVariants}
              className={`inline-block ${char === " " ? "w-[0.6em]" : ""} ${
                glitch && Math.random() > 0.7 ? "text-[#1793D1] translate-x-[2px]" : "text-white"
              }`}
            >
              {char === " " ? "\u00A0" : char}
            </motion.span>
          ))}
        </div>
        <div className="block">
          {LINE2.split("").map((char, i) => (
            <motion.span
              key={`l2-${i}`}
              variants={letterVariants}
              className={`inline-block ${char === " " ? "w-[0.6em]" : ""} ${
                glitch && Math.random() > 0.7 ? "text-[#1793D1] -translate-x-[1px]" : "text-white"
              }`}
            >
              {char === " " ? "\u00A0" : char}
            </motion.span>
          ))}
          <motion.span
            animate={{ opacity: showCursor ? 1 : 0 }}
            transition={{ duration: 0.05 }}
            className="inline-block text-[#1793D1] ml-1"
          >
            _
          </motion.span>
        </div>
      </motion.div>

      <div className="absolute -bottom-6 left-0 flex gap-1.5 opacity-30">
        {[...Array(8)].map((_, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, scale: 0 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 1.2 + i * 0.1, duration: 0.2 }}
            className="w-1.5 h-1.5 bg-[#1793D1] rounded-none"
          />
        ))}
      </div>
    </div>
  );
}
