import type { ReactNode } from "react";
import { useApp } from "../../context/AppContext";

export function ExpertOnly({ children }: { children: ReactNode }) {
  const { mode } = useApp();
  if (mode !== "expert") return null;
  return <>{children}</>;
}

export function BeginnerOnly({ children }: { children: ReactNode }) {
  const { mode } = useApp();
  if (mode !== "beginner") return null;
  return <>{children}</>;
}
