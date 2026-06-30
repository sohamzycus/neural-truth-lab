interface ConfusionMatrixProps {
  matrix: number[][] | undefined;
  label?: string;
}

export function ConfusionMatrix({
  matrix,
  label,
}: ConfusionMatrixProps): React.ReactElement {
  const data = matrix ?? [
    [0, 0],
    [0, 0],
  ];
  const max = Math.max(...data.flat(), 1);

  return (
    <div className="glass-panel p-4">
      {label && (
        <p className="mb-3 text-sm font-medium text-[var(--text-secondary)]">
          {label}
        </p>
      )}
      <div className="grid grid-cols-2 gap-1">
        {data.flat().map((val, i) => (
          <div
            key={i}
            className="flex aspect-square items-center justify-center rounded-lg font-mono text-sm"
            style={{
              background: `rgba(99, 102, 241, ${0.1 + (val / max) * 0.5})`,
            }}
          >
            {val}
          </div>
        ))}
      </div>
      <div className="mt-2 grid grid-cols-2 gap-1 text-center text-[10px] text-[var(--text-muted)]">
        <span>Pred 0</span>
        <span>Pred 1</span>
      </div>
    </div>
  );
}
