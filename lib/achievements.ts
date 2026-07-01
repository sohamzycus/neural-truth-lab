import type { LabId } from "@/lib/constants";
import { LABS } from "@/lib/constants";
import { loadProgress, saveProgress } from "@/lib/progress-storage";

export interface Achievement {
  id: string;
  title: string;
  description: string;
}

export const ACHIEVEMENTS: Record<string, Achievement> = {
  first_truth: {
    id: "first_truth",
    title: "First Truth",
    description: "Complete your first lab",
  },
  truth_seeker: {
    id: "truth_seeker",
    title: "Truth Seeker",
    description: "Complete all four labs",
  },
  memorizer: {
    id: "memorizer",
    title: "Memorizer",
    description: "Generalization gap > 0.3 on tiny data",
  },
  scientist: {
    id: "scientist",
    title: "Scientist",
    description: "Train all four dataset sizes",
  },
};

export function unlockAchievement(id: string): boolean {
  if (typeof window === "undefined") return false;
  const achievement = ACHIEVEMENTS[id];
  if (!achievement) return false;
  const progress = loadProgress();
  if (progress.achievements.includes(id)) return false;
  saveProgress({
    ...progress,
    achievements: [...progress.achievements, id],
  });
  window.dispatchEvent(
    new CustomEvent("ntl-achievement", { detail: achievement })
  );
  window.dispatchEvent(new Event("ntl-progress"));
  return true;
}

export function checkTruthSeeker(completedLabs: LabId[]): void {
  if (completedLabs.length >= LABS.length) {
    unlockAchievement("truth_seeker");
  }
}
