"use client";

import { NeuralNetworkView } from "@/components/visualization/neural-network-view";
import type { NetworkLayer } from "@/lib/lab-schematics";
import { Button } from "@/components/ui/button";

interface LabSchematicPanelProps {
  layers: NetworkLayer[];
  caption: string;
  accentColor?: string;
  toggleLabel?: string;
  onToggle?: () => void;
}

export function LabSchematicPanel({
  layers,
  caption,
  accentColor,
  toggleLabel,
  onToggle,
}: LabSchematicPanelProps): React.ReactElement {
  return (
    <div>
      <NeuralNetworkView layers={layers} caption={caption} accentColor={accentColor} compact />
      {toggleLabel && onToggle ? (
        <Button
          variant="ghost"
          size="sm"
          className="mt-2 h-8 w-full px-2 text-xs"
          onClick={onToggle}
        >
          {toggleLabel}
        </Button>
      ) : null}
    </div>
  );
}
