import type { LabId } from "@/lib/constants";
import { checkTruthSeeker, unlockAchievement } from "@/lib/achievements";

const STORAGE_KEY = "ntl-progress";

export interface UserProgress {
  completedLabs: LabId[];
  achievements: string[];
  lastVisitedLab?: LabId;
}

const DEFAULT_PROGRESS: UserProgress = {
  completedLabs: [],
  achievements: [],
};

export function loadProgress(): UserProgress {
  if (typeof window === "undefined") return DEFAULT_PROGRESS;
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return DEFAULT_PROGRESS;
    return { ...DEFAULT_PROGRESS, ...JSON.parse(raw) };
  } catch {
    return DEFAULT_PROGRESS;
  }
}

export function saveProgress(progress: UserProgress): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(STORAGE_KEY, JSON.stringify(progress));
}

export function markLabComplete(labId: LabId): UserProgress {
  const current = loadProgress();
  if (current.completedLabs.includes(labId)) return current;
  const next: UserProgress = {
    ...current,
    completedLabs: [...current.completedLabs, labId],
    lastVisitedLab: labId,
  };
  saveProgress(next);
  if (next.completedLabs.length === 1) unlockAchievement("first_truth");
  checkTruthSeeker(next.completedLabs);
  if (typeof window !== "undefined") {
    window.dispatchEvent(new Event("ntl-progress"));
  }
  return next;
}

export function getCompletionPercent(totalLabs: number): number {
  const { completedLabs } = loadProgress();
  if (totalLabs === 0) return 0;
  return Math.round((completedLabs.length / totalLabs) * 100);
}
