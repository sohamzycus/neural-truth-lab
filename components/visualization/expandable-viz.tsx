"use client";

import { useEffect, useRef, useState } from "react";
import { ZoomIn, X } from "lucide-react";
import { cn } from "@/lib/utils";

interface ExpandableVizProps {
  label?: string;
  disabled?: boolean;
  children: React.ReactNode;
  expandedChildren?: React.ReactNode;
  className?: string;
  contentClassName?: string;
  expandedClassName?: string;
}

export function ExpandableViz({
  label,
  disabled = false,
  children,
  expandedChildren,
  className,
  contentClassName,
  expandedClassName,
}: ExpandableVizProps): React.ReactElement {
  const dialogRef = useRef<HTMLDialogElement>(null);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const dialog = dialogRef.current;
    if (!dialog) return;
    if (open && !dialog.open) dialog.showModal();
    if (!open && dialog.open) dialog.close();
  }, [open]);

  const close = (): void => setOpen(false);

  return (
    <div className={className}>
      {label ? (
        <p className="mb-1.5 text-xs font-medium text-[var(--text-secondary)] sm:text-sm">
          {label}
        </p>
      ) : null}

      <button
        type="button"
        disabled={disabled}
        onClick={() => !disabled && setOpen(true)}
        className={cn(
          "group relative w-full text-left",
          disabled ? "cursor-default" : "cursor-zoom-in"
        )}
        aria-label={label ? `Expand ${label}` : "Expand visualization"}
      >
        <div className={cn("relative", contentClassName)}>{children}</div>
        {!disabled ? (
          <span className="pointer-events-none absolute inset-0 flex items-end justify-end rounded-lg bg-gradient-to-t from-stone-900/20 via-transparent to-transparent p-2 opacity-0 transition-opacity group-hover:opacity-100 group-focus-visible:opacity-100">
            <span className="flex items-center gap-1 rounded-md bg-white/95 px-2 py-1 text-[10px] font-medium text-stone-800 shadow-sm">
              <ZoomIn className="h-3 w-3" />
              Expand
            </span>
          </span>
        ) : null}
      </button>

      <dialog
        ref={dialogRef}
        onClose={close}
        className="max-h-[95vh] w-[min(100%,44rem)] max-w-[calc(100vw-1.5rem)] rounded-xl border border-[var(--border)] bg-[var(--background-elevated)] p-0 text-[var(--text-primary)] shadow-2xl backdrop:bg-stone-900/40 backdrop:backdrop-blur-sm"
        aria-label={label ?? "Expanded visualization"}
      >
        <div className="flex items-center justify-between gap-3 border-b border-[var(--border)] px-4 py-3">
          <p className="text-sm font-semibold">{label ?? "Visualization"}</p>
          <button
            type="button"
            onClick={close}
            className="rounded-lg border border-[var(--border)] p-1.5 text-[var(--text-muted)] hover:bg-[var(--surface)] hover:text-[var(--text-primary)]"
            aria-label="Close"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
        <div className={cn("p-4", expandedClassName)}>
          {expandedChildren ?? children}
          <p className="mt-2 text-center text-xs text-[var(--text-muted)]">
            Esc to close · click backdrop to dismiss
          </p>
        </div>
      </dialog>
    </div>
  );
}
