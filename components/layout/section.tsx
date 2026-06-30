import { cn } from "@/lib/utils";

interface SectionProps {
  id?: string;
  title?: string;
  eyebrow?: string;
  children: React.ReactNode;
  className?: string;
}

export function Section({
  id,
  title,
  eyebrow,
  children,
  className,
}: SectionProps): React.ReactElement {
  return (
    <section id={id} className={cn("py-16 md:py-24", className)}>
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        {(eyebrow || title) && (
          <header className="mb-8 md:mb-12">
            {eyebrow && (
              <p className="mb-2 text-xs font-medium uppercase tracking-widest text-[var(--text-muted)]">
                {eyebrow}
              </p>
            )}
            {title && (
              <h2 className="text-2xl font-semibold tracking-tight text-[var(--text-primary)] md:text-3xl">
                {title}
              </h2>
            )}
          </header>
        )}
        {children}
      </div>
    </section>
  );
}
