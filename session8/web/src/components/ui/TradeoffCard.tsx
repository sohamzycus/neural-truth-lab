import type { ChronologyEntry } from "../../data/chronology";

export function TradeoffCard({ entry }: { entry: ChronologyEntry }) {
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
