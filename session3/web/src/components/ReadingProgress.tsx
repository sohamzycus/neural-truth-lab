export function ReadingProgress({ progress }: { progress: number }) {
  return (
    <div className="read-progress" aria-hidden>
      <div className="read-progress__bar" style={{ width: `${Math.min(100, progress * 100)}%` }} />
    </div>
  );
}
