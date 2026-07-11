"use client";

interface EpochSliderProps {
  epoch: number;
  maxEpoch: number;
  onChange: (epoch: number) => void;
  disabled?: boolean;
}

export function EpochSlider({
  epoch,
  maxEpoch,
  onChange,
  disabled,
}: EpochSliderProps): React.ReactElement {
  return (
    <div className="glass-panel p-4">
      <div className="mb-2 flex items-center justify-between text-sm">
        <span className="text-[var(--text-secondary)]">Epoch</span>
        <span className="font-mono text-[var(--text-primary)]">
          {epoch} / {maxEpoch || "—"}
        </span>
      </div>
      <input
        type="range"
        min={0}
        max={maxEpoch}
        value={epoch}
        disabled={disabled || maxEpoch === 0}
        onChange={(e) => onChange(Number(e.target.value))}
        className="h-2 w-full cursor-pointer appearance-none rounded-full bg-[var(--surface)] accent-[var(--accent-primary)] disabled:opacity-40"
        aria-label="Training epoch scrubber"
      />
    </div>
  );
}
