import type { LabId } from "@/lib/constants";

export interface NetworkLayer {
  units: number;
  label: string;
}

export interface LabSchematicConfig {
  layers: NetworkLayer[];
  caption: string;
}

export function depthSchematic(collapsed: boolean): LabSchematicConfig {
  if (collapsed) {
    return {
      layers: [{ units: 2, label: "in" }, { units: 1, label: "≡ W₁…W₅" }],
      caption: "Five linear layers collapse into one transformation",
    };
  }
  return {
    layers: [
      { units: 2, label: "in" },
      { units: 8, label: "W₁" },
      { units: 8, label: "W₂" },
      { units: 8, label: "W₃" },
      { units: 8, label: "W₄" },
      { units: 1, label: "W₅" },
    ],
    caption: "5 weight matrices — linear stack (no activation)",
  };
}

export function depthSchematicRelu(): LabSchematicConfig {
  return {
    layers: [
      { units: 2, label: "in" },
      { units: 8, label: "W+σ" },
      { units: 8, label: "W+σ" },
      { units: 8, label: "W+σ" },
      { units: 8, label: "W+σ" },
      { units: 1, label: "out" },
    ],
    caption: "ReLU (σ) between layers — depth is meaningful",
  };
}

export function activationsSchematic(variant: "linear" | "relu"): LabSchematicConfig {
  return {
    layers: [
      { units: 2, label: "in" },
      { units: 16, label: variant === "linear" ? "linear" : "ReLU" },
      { units: 1, label: "σ" },
    ],
    caption:
      variant === "linear"
        ? "Model A — no nonlinearity in the hidden layer"
        : "Model B — ReLU bends the decision surface",
  };
}

export function embeddingsSchematic(): LabSchematicConfig {
  return {
    layers: [
      { units: 4, label: "token" },
      { units: 16, label: "embed" },
      { units: 4, label: "vocab" },
    ],
    caption: "Embedding lookup + softmax — only next-token labels",
  };
}

export function generalizationSchematic(): LabSchematicConfig {
  return {
    layers: [
      { units: 2, label: "in" },
      { units: 8, label: "64" },
      { units: 8, label: "64" },
      { units: 6, label: "32" },
      { units: 1, label: "σ" },
    ],
    caption: "Large MLP — same architecture, varying train set size N",
  };
}

export const LAB_SCHEMATIC_ACCENT: Record<LabId, string> = {
  activations: "var(--lab-activations)",
  depth: "var(--lab-depth)",
  embeddings: "var(--lab-embeddings)",
  generalization: "var(--lab-generalization)",
};
