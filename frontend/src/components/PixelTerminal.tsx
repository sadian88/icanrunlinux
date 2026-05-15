import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";

const COMMANDS: { text: string; color: string }[] = [
  { text: "$ uname -a", color: "text-zinc-400" },
  { text: "Linux penguin 6.8.0-generic #42 SMP x86_64 GNU/Linux", color: "text-emerald-300" },
  { text: "$ lscpu | grep 'Model name'", color: "text-zinc-400" },
  { text: "Model name:          Intel(R) Core(TM) i3-10100", color: "text-emerald-300" },
  { text: "$ free -h", color: "text-zinc-400" },
  { text: "Mem:  3.7Gi total  1.2Gi free", color: "text-emerald-300" },
  { text: "$ neofetch --ascii_distro linux", color: "text-zinc-400" },
  { text: "       .---.", color: "text-emerald-400" },
  { text: "      /     \\", color: "text-emerald-400" },
  { text: "     | o   o |   OS: I Can Run Linux", color: "text-emerald-400" },
  { text: "     |  <    |   Kernel: matching.py", color: "text-emerald-400" },
  { text: "     | \___/ |   Uptime: 3-tier engine", color: "text-emerald-400" },
  { text: "      \_____/", color: "text-emerald-400" },
  { text: "$ ./find_distro.sh --ram=4gb --cpu=i3", color: "text-zinc-400" },
  { text: ">>> Analyzing hardware specs...", color: "text-amber-300" },
  { text: ">>> Querying pgvector database...", color: "text-amber-300" },
  { text: ">>> Match found: Mint, Puppy, antiX", color: "text-emerald-300" },
  { text: "$ _", color: "text-emerald-400" },
];

const LINE_DELAY = 600;

export default function PixelTerminal() {
  const [visibleLines, setVisibleLines] = useState(0);
  const [showCursor, setShowCursor] = useState(true);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (visibleLines < COMMANDS.length) {
      const timer = setTimeout(() => {
        setVisibleLines((prev) => prev + 1);
      }, LINE_DELAY);
      return () => clearTimeout(timer);
    }
  }, [visibleLines]);

  useEffect(() => {
    const interval = setInterval(() => {
      setShowCursor((prev) => !prev);
    }, 530);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [visibleLines]);

  return (
    <div className="w-full max-w-2xl mx-auto">
      {/* Terminal frame */}
      <div className="relative rounded-xl border border-emerald-500/20 bg-black/80 overflow-hidden shadow-2xl shadow-emerald-500/5">
        {/* Scanline overlay */}
        <div
          className="absolute inset-0 pointer-events-none z-20 opacity-[0.03]"
          style={{
            background:
              "repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,0,0,0.3) 2px, rgba(0,0,0,0.3) 4px)",
          }}
        />

        {/* Terminal header */}
        <div className="flex items-center gap-2 px-4 py-2.5 border-b border-emerald-500/10 bg-emerald-500/5">
          <div className="flex gap-1.5">
            <div className="w-2.5 h-2.5 rounded-full bg-red-500/80" />
            <div className="w-2.5 h-2.5 rounded-full bg-amber-500/80" />
            <div className="w-2.5 h-2.5 rounded-full bg-emerald-500/80" />
          </div>
          <span
            className="ml-2 text-[10px] text-emerald-500/60 uppercase tracking-widest"
            style={{ fontFamily: "'Press Start 2P', monospace" }}
          >
            user@linux-matcher:~$
          </span>
        </div>

        {/* Terminal content */}
        <div
          className="px-4 py-4 min-h-[280px] max-h-[320px] overflow-y-auto text-xs sm:text-sm leading-relaxed"
          style={{ fontFamily: "'Press Start 2P', monospace" }}
        >
          <AnimatePresence>
            {COMMANDS.slice(0, visibleLines).map((cmd, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.15 }}
                className={`${cmd.color} mb-1 whitespace-pre-wrap break-all`}
              >
                {cmd.text}
              </motion.div>
            ))}
          </AnimatePresence>

          {/* Blinking cursor on last line */}
          {visibleLines === COMMANDS.length && (
            <motion.span
              animate={{ opacity: showCursor ? 1 : 0 }}
              transition={{ duration: 0.05 }}
              className="text-emerald-400"
            >
              _
            </motion.span>
          )}
          <div ref={bottomRef} />
        </div>

        {/* Bottom glow */}
        <div className="absolute bottom-0 left-0 right-0 h-8 bg-gradient-to-t from-emerald-500/5 to-transparent pointer-events-none" />
      </div>

      {/* Pixel art decoration: small Tux */}
      <div className="flex justify-center mt-6">
        <PixelTux />
      </div>
    </div>
  );
}

function PixelTux() {
  // A simple 12x12 pixel-art Tux rendered with CSS grid
  const pixels = [
    "0000001111000000",
    "0000011111100000",
    "0000111111110000",
    "0001121111211000",
    "0011111111111100",
    "0111111111111110",
    "0111111111111110",
    "0011111111111100",
    "0001111111111000",
    "0000110000110000",
    "0000110000110000",
    "0001111001111000",
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: COMMANDS.length * (LINE_DELAY / 1000) + 0.5, duration: 0.6 }}
      className="flex flex-col items-center gap-2"
    >
      <div className="flex flex-col items-center">
        {pixels.map((row, ri) => (
          <div key={ri} className="flex">
            {row.split("").map((p, pi) => {
              let color = "transparent";
              if (p === "1") color = "#e5e7eb"; // white/gray body
              if (p === "2") color = "#fbbf24"; // amber eyes
              return (
                <div
                  key={pi}
                  className="w-2 h-2 sm:w-2.5 sm:h-2.5"
                  style={{ backgroundColor: color }}
                />
              );
            })}
          </div>
        ))}
      </div>
      <span
        className="text-[8px] text-zinc-600 uppercase tracking-[0.3em] mt-2"
        style={{ fontFamily: "'Press Start 2P', monospace" }}
      >
        Powered by Tux
      </span>
    </motion.div>
  );
}
