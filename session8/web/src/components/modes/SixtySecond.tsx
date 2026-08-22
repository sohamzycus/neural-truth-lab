import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useApp } from "../../context/AppContext";

const STEPS = [
  "Every token asks: who should I listen to?",
  "Q, K, V — query, key, value",
  "Similarity: QKᵀ / √dₖ",
  "Softmax → attention weights",
  "Weighted sum of V → context",
  "Beautiful — but O(n²) pairwise cost",
  "Decode one token at a time → KV cache grows",
  "GQA / MLA compress what we store",
  "Long context needs position tricks + sparsity",
  "Linear / recurrent alternatives trade exact retrieval",
  "That's how attention got here.",
];

export function SixtySecondMode() {
  const { showSixtySecond, setShowSixtySecond } = useApp();

  return (
    <AnimatePresence>
      {showSixtySecond && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-[100] flex items-center justify-center bg-black/80 p-4 backdrop-blur-sm"
          role="dialog"
          aria-modal="true"
          aria-label="60 second explanation"
        >
          <div className="panel panel-glow max-w-lg p-8">
            <h2 className="text-xl font-bold">Attention in 60 Seconds</h2>
            <SixtySecondPlayer onClose={() => setShowSixtySecond(false)} />
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

function SixtySecondPlayer({ onClose }: { onClose: () => void }) {
  const [step, setStep] = useState(0);

  return (
    <>
      <motion.p
        key={step}
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="mt-6 min-h-[4rem] text-lg"
      >
        {STEPS[step]}
      </motion.p>
      <div className="mt-6 flex items-center justify-between">
        <div className="flex gap-1">
          {STEPS.map((_, i) => (
            <div key={i} className={`h-1 w-4 rounded ${i <= step ? "bg-cyan" : "bg-white/15"}`} />
          ))}
        </div>
        <div className="flex gap-2">
          {step < STEPS.length - 1 ? (
            <button type="button" onClick={() => setStep((s) => s + 1)} className="focus-ring text-sm text-cyan">
              Next
            </button>
          ) : (
            <button type="button" onClick={onClose} className="focus-ring text-sm text-cyan">
              Done
            </button>
          )}
          <button type="button" onClick={onClose} className="focus-ring text-sm text-muted">
            Close
          </button>
        </div>
      </div>
    </>
  );
}
