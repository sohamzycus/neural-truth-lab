import { cn } from "@/lib/utils";

interface LabStatProps {
  label: string;
  value: string;
  hint?: string;
  accent?: boolean;
  size?: "sm" | "md";
  className?: string;
}

export function LabStat({
  label,
  value,
  hint,
  accent,
  size = "md",
  className,
}: LabStatProps): React.ReactElement {
  const sm = size === "sm";
  return (
    <div
      className={cn(
        "rounded-lg border border-[var(--border)] bg-[var(--background-elevated)] shadow-sm",
        sm ? "min-w-[4.75rem] px-2 py-1.5" : "min-w-[7rem] px-3 py-2",
        accent && "border-[var(--accent-primary)]/30 bg-[var(--accent-primary)]/5",
        className
      )}
    >
      <p
        className={cn(
          "font-medium uppercase tracking-wider text-[var(--text-muted)]",
          sm ? "text-[9px]" : "text-[10px]"
        )}
      >
        {label}
      </p>
      <p
        className={cn(
          "mt-0.5 font-mono font-semibold tabular-nums",
          sm ? "text-base" : "text-xl",
          accent ? "text-[var(--accent-primary)]" : "text-[var(--text-primary)]"
        )}
      >
        {value}
      </p>
      {hint ? (
        <p className={cn("mt-0.5 text-[var(--text-muted)]", sm ? "text-[9px]" : "text-[10px]")}>
          {hint}
        </p>
      ) : null}
    </div>
  );
}
