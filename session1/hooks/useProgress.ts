"use client";

import { useEffect, useState } from "react";
import { LABS } from "@/lib/constants";
import { ACHIEVEMENTS } from "@/lib/achievements";
import { getCompletionPercent, loadProgress } from "@/lib/progress-storage";

export function useProgress(): {
  percent: number;
  completedCount: number;
  total: number;
  achievements: string[];
} {
  const [percent, setPercent] = useState(0);
  const [achievements, setAchievements] = useState<string[]>([]);

  useEffect(() => {
    const refresh = (): void => {
      setPercent(getCompletionPercent(LABS.length));
      setAchievements(loadProgress().achievements);
    };
    refresh();
    window.addEventListener("ntl-progress", refresh);
    window.addEventListener("storage", refresh);
    return () => {
      window.removeEventListener("ntl-progress", refresh);
      window.removeEventListener("storage", refresh);
    };
  }, []);

  return {
    percent,
    completedCount: Math.round((percent / 100) * LABS.length),
    total: LABS.length,
    achievements,
  };
}

export function useAchievementList(): {
  unlocked: string[];
  all: typeof ACHIEVEMENTS;
} {
  const { achievements } = useProgress();
  return { unlocked: achievements, all: ACHIEVEMENTS };
}
