"use client";

import { useEffect, useState } from "react";
import { LABS } from "@/lib/constants";
import { getCompletionPercent } from "@/lib/progress-storage";

export function useProgress(): {
  percent: number;
  completedCount: number;
  total: number;
} {
  const [percent, setPercent] = useState(0);

  useEffect(() => {
    setPercent(getCompletionPercent(LABS.length));
  }, []);

  return {
    percent,
    completedCount: Math.round((percent / 100) * LABS.length),
    total: LABS.length,
  };
}
