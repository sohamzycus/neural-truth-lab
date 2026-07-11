import { cn } from "@/lib/utils";

interface LabSidebarPanelProps {
  title: string;
  children: React.ReactNode;
  className?: string;
}

export function LabSidebarPanel({
  title,
  children,
  className,
}: LabSidebarPanelProps): React.ReactElement {
  return (
    <div className={cn("rounded-lg border border-[var(--border)] bg-[var(--background-elevated)] p-2 shadow-sm", className)}>
      <p className="mb-1.5 text-[10px] font-semibold uppercase tracking-widest text-[var(--text-muted)]">
        {title}
      </p>
      {children}
    </div>
  );
}
