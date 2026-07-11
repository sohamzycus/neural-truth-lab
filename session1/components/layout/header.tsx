"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";
import {
  ChevronDown,
  Brain,
  HelpCircle,
  Maximize2,
  Share2,
  Trophy,
} from "lucide-react";
import { LABS, SITE } from "@/lib/constants";
import { headerReveal } from "@/animations/variants";
import { cn } from "@/lib/utils";
import { useProgress } from "@/hooks/useProgress";
import { useScrolled } from "@/hooks/useScrolled";
import { useAppUI } from "@/components/providers/app-providers";
import { sharePage } from "@/lib/share";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

function ProgressRing({ percent }: { percent: number }): React.ReactElement {
  const radius = 14;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (percent / 100) * circumference;

  return (
    <div
      className="relative flex h-9 w-9 items-center justify-center"
      aria-label={`${percent}% labs complete`}
    >
      <svg className="h-9 w-9 -rotate-90" viewBox="0 0 36 36">
        <circle
          cx="18"
          cy="18"
          r={radius}
          fill="none"
          stroke="var(--border)"
          strokeWidth="2"
        />
        <circle
          cx="18"
          cy="18"
          r={radius}
          fill="none"
          stroke="var(--accent-primary)"
          strokeWidth="2"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          className="transition-all duration-500"
        />
      </svg>
      <span className="absolute text-[10px] font-mono text-[var(--text-muted)]">
        {percent}
      </span>
    </div>
  );
}

export function Header(): React.ReactElement {
  const pathname = usePathname();
  const scrolled = useScrolled();
  const { percent, achievements } = useProgress();
  const { openShortcuts, openAchievements, toggleFullscreen, isLab } = useAppUI();

  return (
    <motion.header
      initial="hidden"
      animate="visible"
      variants={headerReveal}
      className={cn(
        "glass-header sticky top-0 z-50 transition-[height] duration-200",
        scrolled ? "h-12" : "h-16"
      )}
    >
      <div className="mx-auto flex h-full max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <Link
          href="/"
          className="flex items-center gap-2 text-[var(--text-primary)] transition-opacity hover:opacity-80"
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.92 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.08, duration: 0.4, ease: [0.34, 1.56, 0.64, 1] }}
            className="flex items-center gap-2"
          >
            <Brain className="h-5 w-5 text-[var(--accent-primary)]" />
            <span
              className={cn(
                "font-display font-semibold tracking-tight transition-all",
                scrolled ? "text-sm" : "text-base"
              )}
            >
              {SITE.name}
            </span>
          </motion.div>
        </Link>

        <nav className="hidden items-center gap-1 md:flex">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="sm" className="nav-link-underline gap-1">
                Labs
                <ChevronDown className="h-4 w-4 opacity-60" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="center">
              <DropdownMenuLabel>Four truths</DropdownMenuLabel>
              <DropdownMenuSeparator />
              {LABS.map((lab) => (
                <DropdownMenuItem key={lab.id} asChild>
                  <Link href={lab.href}>
                    <span className={lab.accentClass}>Lab {lab.number}</span>
                    <span>{lab.title}</span>
                  </Link>
                </DropdownMenuItem>
              ))}
              <DropdownMenuSeparator />
              <DropdownMenuItem asChild>
                <Link href="/labs">View all labs</Link>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>

          <Button
            variant="ghost"
            size="sm"
            asChild
            className="nav-link-underline"
          >
            <Link
              href="/about"
              data-active={pathname === "/about" ? "true" : undefined}
              className={cn(
                pathname === "/about" && "text-[var(--text-primary)]"
              )}
            >
              About
            </Link>
          </Button>
        </nav>

        <div className="flex items-center gap-1 sm:gap-2">
          <Button
            variant="ghost"
            size="icon"
            className="h-9 w-9"
            onClick={openAchievements}
            aria-label={`Achievements, ${achievements.length} unlocked`}
          >
            <Trophy className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            className="h-9 w-9"
            onClick={openShortcuts}
            aria-label="Keyboard shortcuts"
          >
            <HelpCircle className="h-4 w-4" />
          </Button>
          {isLab ? (
            <>
              <Button
                variant="ghost"
                size="icon"
                className="hidden h-9 w-9 sm:flex"
                onClick={toggleFullscreen}
                aria-label="Toggle fullscreen"
              >
                <Maximize2 className="h-4 w-4" />
              </Button>
              <Button
                variant="ghost"
                size="icon"
                className="hidden h-9 w-9 sm:flex"
                onClick={() => void sharePage()}
                aria-label="Share this lab"
              >
                <Share2 className="h-4 w-4" />
              </Button>
            </>
          ) : null}
          <ProgressRing percent={percent} />
          <Button variant="secondary" size="sm" className="md:hidden" asChild>
            <Link href="/labs">Labs</Link>
          </Button>
        </div>
      </div>
    </motion.header>
  );
}
