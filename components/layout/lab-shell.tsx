import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

interface LabShellProps {
  labNumber: number;
  title: string;
  subtitle: string;
  accentClass?: string;
  children: React.ReactNode;
}

export function LabShell({
  labNumber,
  title,
  subtitle,
  accentClass,
  children,
}: LabShellProps): React.ReactElement {
  return (
    <div className="min-h-screen">
      <div className="gradient-surface border-b border-[var(--border)]">
        <div className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
          <Button variant="ghost" size="sm" className="mb-8 -ml-2" asChild>
            <Link href="/labs">
              <ArrowLeft className="h-4 w-4" />
              All labs
            </Link>
          </Button>
          <p
            className={cn(
              "mb-3 text-sm font-medium uppercase tracking-widest",
              accentClass ?? "text-[var(--text-muted)]"
            )}
          >
            Lab {String(labNumber).padStart(2, "0")}
          </p>
          <h1 className="max-w-3xl text-4xl font-semibold tracking-tight text-[var(--text-primary)] md:text-5xl">
            {title}
          </h1>
          <p className="mt-4 max-w-2xl text-lg text-[var(--text-secondary)]">
            {subtitle}
          </p>
        </div>
      </div>
      {children}
    </div>
  );
}
