"use client";

import { motion } from "framer-motion";
import type { LabId } from "@/lib/constants";
import { cn } from "@/lib/utils";

const ACCENT: Record<LabId, string> = {
  activations: "var(--lab-activations)",
  depth: "var(--lab-depth)",
  embeddings: "var(--lab-embeddings)",
  generalization: "var(--lab-generalization)",
};

interface TheoryInfographicProps {
  labId: LabId;
  className?: string;
}

export function TheoryInfographic({
  labId,
  className,
}: TheoryInfographicProps): React.ReactElement {
  const accent = ACCENT[labId];

  return (
    <div
      className={cn(
        "relative overflow-hidden rounded-lg border border-[var(--border)] bg-[var(--background)]",
        className
      )}
      aria-hidden
    >
      <svg viewBox="0 0 200 120" className="h-full w-full">
        {labId === "activations" && <ActivationsGraphic accent={accent} />}
        {labId === "depth" && <DepthGraphic accent={accent} />}
        {labId === "embeddings" && <EmbeddingsGraphic accent={accent} />}
        {labId === "generalization" && <GeneralizationGraphic accent={accent} />}
      </svg>
    </div>
  );
}

function ActivationsGraphic({ accent }: { accent: string }): React.ReactElement {
  return (
    <>
      <text x="50" y="14" textAnchor="middle" fontSize="8" fill="#78716c">
        Linear
      </text>
      <text x="150" y="14" textAnchor="middle" fontSize="8" fill="#78716c">
        + ReLU
      </text>
      <line x1="100" y1="20" x2="100" y2="110" stroke="#d6d3d1" strokeWidth="1" />
      {[40, 80].map((cy, i) => (
        <circle key={cy} cx={50} cy={cy} r="18" fill="none" stroke={accent} strokeWidth="1.5" opacity="0.5" />
      ))}
      <motion.line
        x1="20" y1="95" x2="80" y2="35"
        stroke="#a8a29e"
        strokeWidth="2"
        initial={{ pathLength: 0 }}
        animate={{ pathLength: 1 }}
        transition={{ duration: 1.2, repeat: Infinity, repeatType: "reverse", repeatDelay: 0.8 }}
      />
      {[40, 80].map((cy, i) => (
        <circle key={`r${cy}`} cx={150} cy={cy} r="18" fill="none" stroke={accent} strokeWidth="1.5" opacity="0.5" />
      ))}
      <motion.path
        d="M 115 60 Q 150 30, 185 60 Q 150 90, 115 60"
        fill="none"
        stroke={accent}
        strokeWidth="2"
        initial={{ pathLength: 0, opacity: 0.4 }}
        animate={{ pathLength: 1, opacity: 1 }}
        transition={{ duration: 1.4, repeat: Infinity, repeatType: "reverse", repeatDelay: 0.6 }}
      />
    </>
  );
}

function DepthGraphic({ accent }: { accent: string }): React.ReactElement {
  const layers = [30, 55, 80, 105, 130];
  return (
    <>
      <text x="55" y="14" textAnchor="middle" fontSize="8" fill="#78716c">
        5× linear
      </text>
      <text x="145" y="14" textAnchor="middle" fontSize="8" fill="#78716c">
        5× + ReLU
      </text>
      <line x1="100" y1="20" x2="100" y2="110" stroke="#d6d3d1" strokeWidth="1" />
      {layers.map((x, i) => (
        <motion.rect
          key={x}
          x={x - 8}
          y={35 + i * 2}
          width="16"
          height="50"
          rx="2"
          fill={accent}
          opacity={0.15 + i * 0.08}
          animate={{ x: [x - 8, 47, x - 8] }}
          transition={{ duration: 2.5, repeat: Infinity, delay: i * 0.1 }}
        />
      ))}
      <motion.line
        x1="25" y1="90" x2="75" y2="40"
        stroke="#a8a29e"
        strokeWidth="2"
        animate={{ opacity: [0.5, 1, 0.5] }}
        transition={{ duration: 2, repeat: Infinity }}
      />
      {layers.map((x, i) => (
        <g key={`r${x}`}>
          <rect x={x + 62} y={35 + i * 2} width="16" height="12" rx="2" fill={accent} opacity="0.25" />
          <motion.circle
            cx={x + 70}
            cy={55 + i * 2}
            r="3"
            fill={accent}
            animate={{ scale: [0.8, 1.2, 0.8] }}
            transition={{ duration: 1.2, repeat: Infinity, delay: i * 0.15 }}
          />
        </g>
      ))}
      <motion.path
        d="M 118 70 Q 150 40, 182 70"
        fill="none"
        stroke={accent}
        strokeWidth="2"
        animate={{ pathLength: [0.3, 1, 0.3] }}
        transition={{ duration: 2, repeat: Infinity }}
      />
    </>
  );
}

function EmbeddingsGraphic({ accent }: { accent: string }): React.ReactElement {
  const clusters = [
    { cx: 45, cy: 45, color: "#1d4ed8" },
    { cx: 55, cy: 55, color: "#1d4ed8" },
    { cx: 100, cy: 70, color: "#15803d" },
    { cx: 110, cy: 80, color: "#15803d" },
    { cx: 155, cy: 40, color: "#b45309" },
    { cx: 145, cy: 50, color: "#b45309" },
  ];
  return (
    <>
      <text x="100" y="14" textAnchor="middle" fontSize="8" fill="#78716c">
        Next-token → clusters
      </text>
      {Array.from({ length: 12 }, (_, i) => (
        <motion.circle
          key={i}
          r="3"
          fill="#a8a29e"
          initial={{ cx: 30 + (i % 4) * 45, cy: 30 + Math.floor(i / 4) * 35 }}
          animate={{
            cx: clusters[i % clusters.length].cx + (i % 3) * 4,
            cy: clusters[i % clusters.length].cy + (i % 2) * 4,
          }}
          transition={{ duration: 2.5, repeat: Infinity, repeatType: "reverse", delay: i * 0.08 }}
        />
      ))}
      {clusters.map((c, i) => (
        <motion.circle
          key={i}
          cx={c.cx}
          cy={c.cy}
          r="14"
          fill="none"
          stroke={c.color}
          strokeWidth="1"
          strokeDasharray="3 2"
          initial={{ opacity: 0 }}
          animate={{ opacity: [0, 0.6, 0.6] }}
          transition={{ duration: 2, delay: 1 + i * 0.2, repeat: Infinity, repeatType: "reverse", repeatDelay: 1 }}
        />
      ))}
    </>
  );
}

function GeneralizationGraphic({ accent }: { accent: string }): React.ReactElement {
  return (
    <>
      <text x="55" y="14" textAnchor="middle" fontSize="8" fill="#78716c">
        N=20
      </text>
      <text x="145" y="14" textAnchor="middle" fontSize="8" fill="#78716c">
        N=2000
      </text>
      <line x1="100" y1="20" x2="100" y2="110" stroke="#d6d3d1" strokeWidth="1" />
      <motion.path
        d="M 15 95 L 40 70 L 55 55 L 70 45"
        fill="none"
        stroke={accent}
        strokeWidth="2"
        initial={{ pathLength: 0 }}
        animate={{ pathLength: 1 }}
        transition={{ duration: 1.5, repeat: Infinity, repeatType: "reverse" }}
      />
      <motion.path
        d="M 15 95 L 40 80 L 55 72 L 70 68"
        fill="none"
        stroke="#b91c1c"
        strokeWidth="2"
        strokeDasharray="4 2"
        initial={{ pathLength: 0 }}
        animate={{ pathLength: 1 }}
        transition={{ duration: 1.5, repeat: Infinity, repeatType: "reverse", delay: 0.2 }}
      />
      <motion.path
        d="M 115 90 L 140 75 L 155 68 L 185 62"
        fill="none"
        stroke={accent}
        strokeWidth="2"
        animate={{ opacity: [0.6, 1, 0.6] }}
        transition={{ duration: 2, repeat: Infinity }}
      />
      <motion.path
        d="M 115 92 L 140 78 L 155 72 L 185 68"
        fill="none"
        stroke="#b91c1c"
        strokeWidth="1.5"
        strokeDasharray="4 2"
        animate={{ opacity: [0.6, 1, 0.6] }}
        transition={{ duration: 2, repeat: Infinity, delay: 0.3 }}
      />
      <motion.rect
        x="25" y="50" width="50" height="25"
        fill={accent}
        opacity="0.08"
        animate={{ height: [25, 40, 25], y: [50, 35, 50] }}
        transition={{ duration: 2, repeat: Infinity }}
      />
    </>
  );
}
