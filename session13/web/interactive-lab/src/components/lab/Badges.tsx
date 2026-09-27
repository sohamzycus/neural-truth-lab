export function MeasuredBadge({ className = "" }: { className?: string }) {
  return (
    <span className={`inline-flex items-center gap-1 text-[10px] uppercase tracking-wider text-sky-300 ${className}`}>
      <span className="text-sky-400">●</span> Measured
    </span>
  );
}
export function EstimatedBadge({ className = "" }: { className?: string }) {
  return (
    <span className={`inline-flex items-center gap-1 text-[10px] uppercase tracking-wider text-amber-200/90 ${className}`}>
      <span className="text-amber-400">◇</span> Estimated
    </span>
  );
}
