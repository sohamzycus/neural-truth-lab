import type { ChronologyEntry } from "../../data/chronology";
import { getNextEntry } from "../../data/chronology";
import { useApp } from "../../context/AppContext";
import { ExpertOnly } from "./ExpertOnly";

export function TradeoffCard({ entry }: { entry: ChronologyEntry }) {
  const { mode } = useApp();
  const next = getNextEntry(entry.id);
  const nextFix = entry.nextFix ?? (next ? `→ ${next.title}: ${next.motivation}` : undefined);

  return (
    <div className="panel panel-glow p-5 transition-shadow hover:shadow-md">
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div>
          <h3 className="font-serif text-lg font-semibold">{entry.title}</h3>
          <ExpertOnly>
            <p className="text-sm text-muted">{entry.fullName}</p>
          </ExpertOnly>
        </div>
        <span className="rounded-full bg-[var(--color-surface-2)] px-2 py-1 text-[10px] uppercase tracking-wide text-muted">
          {entry.category}
        </span>
      </div>

      <div className="mt-4 rounded-lg border border-theme bg-[var(--color-surface-2)] p-4 text-sm">
        <p className="text-[10px] font-semibold uppercase tracking-wider text-violet">Causal chain</p>
        <ol className="mt-2 space-y-2 text-muted">
          <li><span className="text-text font-medium">Problem:</span> {entry.motivation}</li>
          {mode === "expert" && (
            <li><span className="text-text font-medium">Why change:</span> {entry.mechanism}</li>
          )}
          <li><span className="trade-plus">Cheaper / better:</span> {entry.buys}</li>
          <li><span className="trade-minus">Worse / trade-off:</span> {entry.givesUp}</li>
          {nextFix && (
            <li><span className="text-[var(--color-accent)]">Next paper fixes:</span> {nextFix}</li>
          )}
        </ol>
      </div>

      {mode === "expert" && (
        <>
          <dl className="mt-4 grid gap-3 text-sm sm:grid-cols-2 expert-detail">
            <div>
              <dt className="trade-when font-semibold">→ When to use</dt>
              <dd className="mt-1 text-muted">{entry.chooseWhen}</dd>
            </div>
          </dl>

          <div className="expert-detail mt-4 grid gap-2 border-t border-theme pt-4 text-xs font-mono sm:grid-cols-3">
            <div><span className="text-muted">Complexity:</span> {entry.complexity}</div>
            <div><span className="text-muted">KV impact:</span> {entry.kvImpact}</div>
            <div><span className="text-muted">Context:</span> {entry.contextImpact}</div>
          </div>
        </>
      )}

      <a
        href={entry.sourceUrl}
        target="_blank"
        rel="noopener noreferrer"
        className="focus-ring mt-4 inline-flex text-xs text-[var(--color-accent)] hover:underline"
      >
        {entry.authors} · {entry.venue} · {entry.date}
      </a>
    </div>
  );
}
