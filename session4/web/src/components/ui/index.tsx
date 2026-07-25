import type { ReactNode } from "react";

export function StatTile({
  label,
  value,
  hint,
}: {
  label: string;
  value: string | number;
  hint?: string;
}) {
  return (
    <div className="panel p-4">
      <div className="text-[11px] uppercase tracking-[0.16em] text-[var(--color-muted)]">{label}</div>
      <div className="mt-2 font-mono text-2xl tracking-tight text-[var(--color-text)]">{value}</div>
      {hint ? <div className="mt-1 text-sm text-[var(--color-muted)]">{hint}</div> : null}
    </div>
  );
}

export function MetricCounter({ value, label }: { value: string; label: string }) {
  return (
    <div className="panel px-4 py-5 text-center">
      <div className="font-mono text-3xl text-[var(--color-accent)]">{value}</div>
      <div className="mt-2 text-sm text-[var(--color-muted)]">{label}</div>
    </div>
  );
}

export function ExpandableCard({
  title,
  open,
  onToggle,
  children,
}: {
  title: string;
  open: boolean;
  onToggle: () => void;
  children: ReactNode;
}) {
  const panelId = `expand-${title.replace(/\s+/g, "-").toLowerCase()}`;
  return (
    <div className="panel overflow-hidden">
      <button
        type="button"
        onClick={onToggle}
        aria-expanded={open}
        aria-controls={panelId}
        className="flex w-full items-center justify-between gap-4 px-5 py-4 text-left transition hover:bg-white/[0.02]"
      >
        <span className="font-medium">{title}</span>
        <span className="font-mono text-xs text-[var(--color-muted)]" aria-hidden>
          {open ? "−" : "+"}
        </span>
      </button>
      {open ? (
        <div id={panelId} className="border-t border-[var(--color-border)] px-5 py-4 text-sm text-[var(--color-muted)]">
          {children}
        </div>
      ) : null}
    </div>
  );
}

export function ObservationCard({
  title,
  issues,
  text,
  meta,
}: {
  title: string;
  issues: string[];
  text: string;
  meta?: Record<string, string>;
}) {
  return (
    <article className="panel flex flex-col gap-3 p-5">
      <div className="flex flex-wrap items-start justify-between gap-2">
        <h3 className="text-base font-medium text-[var(--color-text)]">{title}</h3>
        <div className="flex flex-wrap gap-1.5">
          {issues.map((issue) => (
            <span
              key={issue}
              className="rounded border border-[var(--color-border)] px-2 py-0.5 font-mono text-[10px] uppercase tracking-wide text-[var(--color-warn)]"
            >
              {issue}
            </span>
          ))}
        </div>
      </div>
      <pre className="overflow-x-auto whitespace-pre-wrap rounded-md bg-black/30 p-3 font-mono text-xs leading-relaxed text-[var(--color-text)]/90">
        {text}
      </pre>
      {meta ? (
        <dl className="grid gap-1 text-xs text-[var(--color-muted)]">
          {Object.entries(meta).map(([k, v]) => (
            <div key={k} className="flex gap-2">
              <dt className="font-mono uppercase tracking-wider">{k}</dt>
              <dd>{v}</dd>
            </div>
          ))}
        </dl>
      ) : null}
    </article>
  );
}

export function BeforeAfter({
  raw,
  clean,
  transforms,
}: {
  raw: string;
  clean: string;
  transforms: string[];
}) {
  return (
    <div className="grid gap-4 lg:grid-cols-2">
      <div className="panel p-4">
        <div className="mb-2 text-[11px] uppercase tracking-[0.16em] text-[var(--color-danger)]">Raw</div>
        <pre className="whitespace-pre-wrap font-mono text-xs leading-relaxed text-[var(--color-muted)]">{raw}</pre>
      </div>
      <div className="panel p-4">
        <div className="mb-2 text-[11px] uppercase tracking-[0.16em] text-[var(--color-ok)]">Clean</div>
        <pre className="whitespace-pre-wrap font-mono text-xs leading-relaxed text-[var(--color-text)]">{clean}</pre>
      </div>
      <div className="lg:col-span-2 flex flex-wrap gap-2">
        {transforms.map((t) => (
          <span key={t} className="rounded-full border border-[var(--color-border)] px-3 py-1 text-xs text-[var(--color-accent)]">
            {t}
          </span>
        ))}
      </div>
    </div>
  );
}

export function PipelineNode({
  name,
  active,
  onClick,
}: {
  name: string;
  active: boolean;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-pressed={active}
      className={`w-full rounded-lg border px-4 py-3 text-left text-sm transition ${
        active
          ? "border-[var(--color-accent)] bg-[var(--color-accent)]/10 text-[var(--color-text)]"
          : "border-[var(--color-border)] bg-[var(--color-surface)] text-[var(--color-muted)] hover:border-white/20 hover:text-[var(--color-text)]"
      }`}
    >
      {name}
    </button>
  );
}

export function InsightTile({
  label,
  value,
  detail,
  why,
}: {
  label: string;
  value: string;
  detail: string;
  why: string;
}) {
  return (
    <article className="panel p-5">
      <div className="text-[11px] uppercase tracking-[0.16em] text-[var(--color-muted)]">{label}</div>
      <div className="mt-2 text-lg font-medium text-[var(--color-text)]">{value}</div>
      <p className="mt-2 text-sm text-[var(--color-muted)]">{detail}</p>
      <p className="mt-3 text-xs text-[var(--color-accent)]">{why}</p>
    </article>
  );
}
