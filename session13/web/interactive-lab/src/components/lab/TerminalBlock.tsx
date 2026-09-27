import { MeasuredBadge } from "./Badges";

export function TerminalBlock({ title, lines }: { title: string; lines: string[] }) {
  return (
    <div className="overflow-hidden rounded-lg border border-white/10 bg-[#0d1117] font-mono text-xs">
      <div className="flex items-center justify-between border-b border-white/10 px-3 py-2 text-[10px] text-white/50">
        <span>{title}</span>
        <MeasuredBadge />
      </div>
      <pre className="max-h-64 overflow-auto p-3 leading-relaxed text-emerald-100/90">{lines.join("\n")}</pre>
    </div>
  );
}
