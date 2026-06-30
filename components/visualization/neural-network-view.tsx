"use client";

import { motion } from "framer-motion";

interface NeuralNetworkViewProps {
  collapsed?: boolean;
  layerCount?: number;
  hiddenUnits?: number;
}

export function NeuralNetworkView({
  collapsed = false,
  layerCount = 5,
  hiddenUnits = 8,
}: NeuralNetworkViewProps): React.ReactElement {
  const layers = collapsed
    ? [{ inputs: 2, units: 1, label: "≡ 1 layer" }]
    : [
        { inputs: 2, units: hiddenUnits, label: "W₁" },
        ...Array.from({ length: layerCount - 2 }, (_, i) => ({
          inputs: hiddenUnits,
          units: hiddenUnits,
          label: `W${i + 2}`,
        })),
        { inputs: hiddenUnits, units: 1, label: `W${layerCount}` },
      ];

  return (
    <div className="glass-panel p-6">
      <p className="mb-4 text-sm font-medium text-[var(--text-primary)]">
        Network schematic
      </p>
      <div className="flex items-center justify-center gap-2 overflow-x-auto py-4 md:gap-4">
        {layers.map((layer, li) => (
          <motion.div
            key={`${collapsed}-${li}`}
            className="flex flex-col items-center gap-2"
            layout
            initial={false}
            animate={{
              scale: collapsed ? 1.05 : 1,
              opacity: 1,
            }}
            transition={{ type: "spring", stiffness: 260, damping: 24 }}
          >
            <div className="flex flex-col items-center gap-1">
              {Array.from({ length: Math.min(layer.units, 6) }).map((_, ni) => (
                <div
                  key={ni}
                  className="h-2.5 w-2.5 rounded-full bg-[var(--lab-depth)] shadow-[0_0_8px_rgba(6,182,212,0.5)]"
                />
              ))}
              {layer.units > 6 && (
                <span className="text-[10px] text-[var(--text-muted)]">+{layer.units - 6}</span>
              )}
            </div>
            <span className="font-mono text-[10px] text-[var(--text-muted)]">{layer.label}</span>
            {li < layers.length - 1 && (
              <span className="hidden text-[var(--text-muted)] md:inline">→</span>
            )}
          </motion.div>
        ))}
      </div>
      <p className="mt-2 text-center text-xs text-[var(--text-muted)]">
        {collapsed
          ? "Five linear layers collapse into one transformation"
          : `${layerCount} weight matrices — linear stack`}
      </p>
    </div>
  );
}
