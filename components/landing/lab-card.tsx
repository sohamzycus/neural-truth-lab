import Link from "next/link";
import { Zap, Layers, Sparkles, TrendingUp } from "lucide-react";
import { cn } from "@/lib/utils";
import type { LabId } from "@/lib/constants";

const ICONS: Record<LabId, React.ComponentType<{ className?: string }>> = {
  activations: Zap,
  depth: Layers,
  embeddings: Sparkles,
  generalization: TrendingUp,
};

interface LabCardLab {
  id: LabId;
  number: number;
  title: string;
  description: string;
  href: string;
  accentClass: string;
  borderClass: string;
}

interface LabCardProps {
  lab: LabCardLab;
}

export function LabCard({ lab }: LabCardProps): React.ReactElement {
  const Icon = ICONS[lab.id];

  return (
    <Link
      href={lab.href}
      className={cn(
        "glass-panel group flex flex-col border-l-4 p-6 transition-all duration-300",
        "hover:-translate-y-1 hover:border-[var(--border-strong)] hover:shadow-[0_12px_40px_rgba(0,0,0,0.5)]",
        lab.borderClass
      )}
    >
      <div
        className={cn(
          "mb-4 flex h-10 w-10 items-center justify-center rounded-xl bg-[var(--surface)] transition-transform duration-300 group-hover:scale-110",
          lab.accentClass
        )}
      >
        <Icon className="h-5 w-5" />
      </div>
      <p className="text-xs font-medium uppercase tracking-wider text-[var(--text-muted)]">
        Lab {String(lab.number).padStart(2, "0")}
      </p>
      <h3 className="mt-1 text-lg font-semibold text-[var(--text-primary)]">
        {lab.title}
      </h3>
      <p className="mt-2 flex-1 text-sm leading-relaxed text-[var(--text-secondary)]">
        {lab.description}
      </p>
      <span
        className={cn(
          "mt-4 text-sm font-medium transition-colors",
          lab.accentClass
        )}
      >
        Open lab →
      </span>
    </Link>
  );
}
