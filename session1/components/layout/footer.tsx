"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { SITE } from "@/lib/constants";

const STACK = [
  "Next.js",
  "TensorFlow.js",
  "Framer Motion",
] as const;

export function Footer(): React.ReactElement | null {
  const pathname = usePathname();
  if (pathname.startsWith("/lab/")) return null;

  return (
    <footer className="border-t border-[var(--border)] bg-[var(--background-elevated)]">
      <div className="mx-auto flex max-w-7xl flex-col gap-6 px-4 py-12 sm:px-6 lg:px-8">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="font-display font-semibold text-[var(--text-primary)]">{SITE.name}</p>
            <p className="mt-1 text-sm text-[var(--text-secondary)]">
              Built with TensorFlow.js — all training runs in your browser.
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            {STACK.map((tech) => (
              <span
                key={tech}
                className="rounded-full border border-[var(--border)] bg-[var(--surface)] px-3 py-1 text-xs text-[var(--text-muted)]"
              >
                {tech}
              </span>
            ))}
          </div>
        </div>
        <div className="flex flex-col gap-2 border-t border-[var(--border)] pt-6 text-sm text-[var(--text-muted)] sm:flex-row sm:justify-between">
          <p>© {new Date().getFullYear()} Neural Truth Lab</p>
          <Link
            href="/about"
            className="transition-colors hover:text-[var(--text-secondary)]"
          >
            About & credits
          </Link>
        </div>
      </div>
    </footer>
  );
}
