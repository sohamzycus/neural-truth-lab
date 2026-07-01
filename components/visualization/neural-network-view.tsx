"use client";

import { motion } from "framer-motion";
import type { NetworkLayer } from "@/lib/lab-schematics";

interface NeuralNetworkViewProps {
  layers: NetworkLayer[];
  caption?: string;
  accentColor?: string;
  compact?: boolean;
}

export function NeuralNetworkView({
  layers,
  caption,
  accentColor = "var(--lab-depth)",
  compact = false,
}: NeuralNetworkViewProps): React.ReactElement {
  const dot = compact ? "h-2 w-2" : "h-2.5 w-2.5";
  const maxDots = compact ? 5 : 6;

  return (
    <div className={compact ? "rounded-lg border border-[var(--border)] bg-[var(--background-elevated)] p-3" : "glass-panel p-6"}>
      {!compact ? (
        <p className="mb-2 text-xs font-medium text-[var(--text-primary)]">
          Network schematic
        </p>
      ) : null}
      <div className="flex items-center justify-center gap-1.5 overflow-x-auto scrollbar-hide py-2 md:gap-2">
        {layers.map((layer, li) => (
          <motion.div
            key={`${layer.label}-${li}`}
            className="flex flex-col items-center gap-1"
            layout
            initial={false}
            transition={{ type: "spring", stiffness: 260, damping: 24 }}
          >
            <div className="flex flex-col items-center gap-0.5">
              {Array.from({ length: Math.min(layer.units, maxDots) }).map((_, ni) => (
                <div
                  key={ni}
                  className={`${dot} rounded-full`}
                  style={{
                    background: accentColor,
                    boxShadow: `0 0 6px color-mix(in srgb, ${accentColor} 50%, transparent)`,
                  }}
                />
              ))}
              {layer.units > maxDots ? (
                <span className="text-[9px] text-[var(--text-muted)]">
                  +{layer.units - maxDots}
                </span>
              ) : null}
            </div>
            <span className="font-mono text-[9px] text-[var(--text-muted)]">
              {layer.label}
            </span>
            {li < layers.length - 1 ? (
              <span className="hidden text-[10px] text-[var(--text-muted)] sm:inline">→</span>
            ) : null}
          </motion.div>
        ))}
      </div>
      {caption ? (
        <p className="mt-1.5 text-center text-[10px] leading-snug text-[var(--text-muted)]">
          {caption}
        </p>
      ) : null}
    </div>
  );
}
