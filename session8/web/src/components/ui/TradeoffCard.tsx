import type { ChronologyEntry } from "../../data/chronology";
import { getNextEntry } from "../../data/chronology";

export function TradeoffCard({ entry }: { entry: ChronologyEntry }) {
  const next = getNextEntry(entry.id);
  const nextFix = entry.nextFix ?? (next ? `→ ${next.title}: ${next.motivation}` : undefined);

  return (
    <div className="panel panel-glow p-5">
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div>
          <h3 className="text-lg font-bold">{entry.title}</h3>
          <p className="text-sm text-muted">{entry.fullName}</p>
        </div>
        <span className="rounded-full bg-white/5 px-2 py-1 text-[10px] uppercase tracking-wide text-muted">
          {entry.category}
        </span>
      </div>

      <div className="mt-4 rounded-lg border border-white/8 bg-black/20 p-4 text-sm">
        <p className="text-[10px] font-semibold uppercase tracking-wider text-violet">Causal chain</p>
        <ol className="mt-2 space-y-2 text-muted">
          <li><span className="text-text">Problem:</span> {entry.motivation}</li>
          <li><span className="text-text">Why change:</span> {entry.mechanism}</li>
          <li><span className="trade-plus">Cheaper / better:</span> {entry.buys}</li>
          <li><span className="trade-minus">Worse / trade-off:</span> {entry.givesUp}</li>
          {nextFix && <li><span className="text-cyan">Next paper fixes:</span> {nextFix}</li>}
        </ol>
      </div>

      <dl className="mt-4 grid gap-3 text-sm sm:grid-cols-2">
        <div>
          <dt className="trade-plus font-semibold">+ What it buys</dt>
          <dd className="mt-1 text-muted">{entry.buys}</dd>
        </div>
        <div>
          <dt className="trade-minus font-semibold">− What it gives up</dt>
          <dd className="mt-1 text-muted">{entry.givesUp}</dd>
        </div>
        <div className="sm:col-span-2">
          <dt className="trade-when font-semibold">→ When to use</dt>
          <dd className="mt-1 text-muted">{entry.chooseWhen}</dd>
        </div>
      </dl>

      <div className="mt-4 grid gap-2 border-t border-white/8 pt-4 text-xs font-mono sm:grid-cols-3">
        <div><span className="text-muted">Complexity:</span> {entry.complexity}</div>
        <div><span className="text-muted">KV impact:</span> {entry.kvImpact}</div>
        <div><span className="text-muted">Context:</span> {entry.contextImpact}</div>
      </div>

      <a
        href={entry.sourceUrl}
        target="_blank"
        rel="noopener noreferrer"
        className="focus-ring mt-4 inline-flex text-xs text-cyan hover:underline"
      >
        {entry.authors} · {entry.venue} · {entry.date}
      </a>
    </div>
  );
}
