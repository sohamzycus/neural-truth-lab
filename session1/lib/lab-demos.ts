import type { LabId } from "@/lib/constants";

export interface LabDemoContent {
  sessionConcept: string;
  proving: string;
  watchFor: readonly string[];
  beforeLabel: string;
  afterLabel: string;
}

export const LAB_DEMOS: Record<LabId, LabDemoContent> = {
  activations: {
    sessionConcept: "WHY NN? · Real world is non-linear",
    proving:
      "A linear model is one straight boundary. ReLU is the smallest change that makes depth nonlinear.",
    watchFor: [
      "Model A: boundary stays a line — cannot wrap the inner ring",
      "Model B: same data & optimizer — boundary curves after ReLU",
      "Accuracy jumps when nonlinearity enters the stack",
    ],
    beforeLabel: "Without activation (linear)",
    afterLabel: "With ReLU (nonlinear)",
  },
  depth: {
    sessionConcept: "LAYERS · More depth only helps with nonlinearity",
    proving:
      "Five linear layers multiply into one matrix — depth adds zero power until activations break linearity.",
    watchFor: [
      "1 linear vs 5 linear: identical decision surface",
      "Weight product W₅W₄W₃W₂W₁ collapses to a single 2×2 matrix",
      "5 layers + ReLU: depth finally bends the boundary",
    ],
    beforeLabel: "Depth without activation",
    afterLabel: "Depth with ReLU",
  },
  embeddings: {
    sessionConcept: "EMBEDDINGS · Vectors learn meaning from context",
    proving:
      "The model only predicts the next token — never told which words are similar.",
    watchFor: [
      "Animals, fruits, and verbs cluster in PCA without category labels",
      "Cosine neighbors share template slots (<animal> <verb> <fruit>)",
      "Meaning emerges from co-occurrence, not supervision",
    ],
    beforeLabel: "Random init (no structure)",
    afterLabel: "After next-token training",
  },
  generalization: {
    sessionConcept: "LOSS · Train vs validation tells the story",
    proving:
      "A large model on tiny data drives train loss down while validation stays high — more data forces the true boundary.",
    watchFor: [
      "N=20: gap widens — memorizing noise",
      "N grows: train & val losses converge",
      "Decision boundary smooths as data regularizes the model",
    ],
    beforeLabel: "Tiny data (memorize)",
    afterLabel: "Large data (generalize)",
  },
};

/** Epoch budget per dataset size — large N is expensive per epoch in-browser */
export const GENERALIZATION_EPOCHS: Record<number, number> = {
  20: 80,
  200: 50,
  2000: 30,
  20000: 18,
};

export const GENERALIZATION_SNAPSHOT_EVERY = 5;
