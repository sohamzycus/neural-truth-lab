import { cn } from "@/lib/utils";
import { LabDemoBanner } from "@/components/labs/lab-demo-banner";
import type { LabId } from "@/lib/constants";
import type { LabDemoContent } from "@/lib/lab-demos";

interface LabWorkspaceProps {
  labId: LabId;
  experiment: string;
  problem: string;
  solution: string;
  accentClass?: string;
  demo: LabDemoContent;
  stats?: React.ReactNode;
  sidebar: React.ReactNode;
  children: React.ReactNode;
  charts?: React.ReactNode;
  insight?: React.ReactNode;
  className?: string;
}

export function LabWorkspace({
  labId,
  experiment,
  problem,
  solution,
  accentClass,
  demo,
  stats,
  sidebar,
  children,
  charts,
  insight,
  className,
}: LabWorkspaceProps): React.ReactElement {
  return (
    <div
      className={cn(
        "flex h-full min-h-0 flex-col gap-2 px-2 py-2 sm:px-3",
        className
      )}
    >
      <LabDemoBanner
        labId={labId}
        demo={demo}
        experiment={experiment}
        problem={problem}
        solution={solution}
        accentClass={accentClass}
        stats={stats}
        className="shrink-0"
      />

      <div
        className={cn(
          "grid min-h-0 flex-1 gap-2 overflow-hidden",
          "lg:grid-cols-[minmax(200px,240px)_1fr]"
        )}
      >
        <aside className="scrollbar-hide flex max-h-[34vh] min-h-0 flex-col gap-2 overflow-y-auto lg:max-h-none">
          {sidebar}
        </aside>

        <div className="scrollbar-hide flex min-h-0 flex-col gap-2 overflow-hidden lg:overflow-y-auto">
          <div className="shrink-0">{children}</div>

          {charts ? (
            <div className="shrink-0 border-t border-[var(--border)] bg-[var(--background-elevated)] p-2">
              <div className="grid gap-2 sm:grid-cols-2">{charts}</div>
            </div>
          ) : null}

          {insight ? <div className="shrink-0 pb-1">{insight}</div> : null}
        </div>
      </div>
    </div>
  );
}
