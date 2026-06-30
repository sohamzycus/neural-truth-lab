import type { LabId } from "@/lib/constants";

export interface LabMeta {
  id: LabId;
  slug: string;
  number: number;
  title: string;
  headline: string;
  description: string;
  href: string;
}

export interface UserProgress {
  completedLabs: LabId[];
  achievements: string[];
  lastVisitedLab?: LabId;
}
