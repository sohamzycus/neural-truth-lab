"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { kernelLabels } from "@/training/weight-collapse";
import { WeightMatrix } from "@/components/visualization/weight-matrix";
import { Button } from "@/components/ui/button";

interface WeightCollapsePanelProps {
  matrices: number[][][] | undefined;
  combined: number[][] | undefined;
}

export function WeightCollapsePanel({
  matrices,
  combined,
}: WeightCollapsePanelProps): React.ReactElement | null {
  const [collapsed, setCollapsed] = useState(false);
  const [animating, setAnimating] = useState(false);

  if (!matrices?.length || !combined) return null;

  const labels = kernelLabels(matrices);

  const playCollapse = (): void => {
    setAnimating(true);
    setCollapsed(false);
    setTimeout(() => setCollapsed(true), 600);
    setTimeout(() => setAnimating(false), 1200);
  };

  return (
    <div className="glass-panel p-6">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-sm font-medium text-[var(--text-primary)]">
            Weight collapse
          </p>
          <p className="mt-1 font-mono text-xs text-[var(--text-muted)]">
            W = W₅ × W₄ × W₃ × W₂ × W₁
          </p>
        </div>
        <Button variant="secondary" size="sm" onClick={playCollapse} disabled={animating}>
          {animating ? "Collapsing…" : "Animate collapse"}
        </Button>
      </div>

      <AnimatePresence mode="wait">
        {!collapsed ? (
          <motion.div
            key="expanded"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5"
          >
            {matrices.map((m, i) => (
              <motion.div
                key={labels[i]}
                layout
                animate={animating ? { x: 0, scale: 0.85 } : {}}
                transition={{ duration: 0.6, ease: [0.4, 0, 0.2, 1] }}
              >
                <WeightMatrix matrix={m} label={labels[i]} />
              </motion.div>
            ))}
          </motion.div>
        ) : (
          <motion.div
            key="collapsed"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="mx-auto max-w-xs"
          >
            <WeightMatrix matrix={combined} label="W combined (product)" />
            <p className="mt-4 text-center text-sm font-medium text-[var(--lab-depth)]">
              5 layers. 0 activations. ≡ 1 linear layer.
            </p>
          </motion.div>
        )}
      </AnimatePresence>

      {collapsed && (
        <Button
          variant="ghost"
          size="sm"
          className="mt-4"
          onClick={() => setCollapsed(false)}
        >
          Show W₁…W₅ again
        </Button>
      )}
    </div>
  );
}
