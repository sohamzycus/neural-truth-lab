"use client";

import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
} from "react";
import { usePathname } from "next/navigation";
import { AchievementsPanel } from "@/components/layout/achievements-panel";
import { AchievementToast } from "@/components/layout/achievement-toast";
import { KeyboardShortcutsDialog } from "@/components/layout/keyboard-shortcuts-dialog";
import { useFullscreen } from "@/hooks/useFullscreen";
import { useKeyboardShortcuts } from "@/hooks/useKeyboardShortcuts";

interface AppUIContextValue {
  openShortcuts: () => void;
  openAchievements: () => void;
  toggleFullscreen: () => void;
  isLab: boolean;
}

const AppUIContext = createContext<AppUIContextValue | null>(null);

export function useAppUI(): AppUIContextValue {
  const ctx = useContext(AppUIContext);
  if (!ctx) throw new Error("useAppUI must be used within AppProviders");
  return ctx;
}

export function AppProviders({
  children,
}: {
  children: React.ReactNode;
}): React.ReactElement {
  const pathname = usePathname();
  const isLab = pathname.startsWith("/lab/");
  const [shortcutsOpen, setShortcutsOpen] = useState(false);
  const [achievementsOpen, setAchievementsOpen] = useState(false);
  const { toggle: toggleFullscreen, exit: exitFullscreen } =
    useFullscreen("main");

  const closeAll = useCallback(() => {
    setShortcutsOpen(false);
    setAchievementsOpen(false);
    exitFullscreen();
  }, [exitFullscreen]);

  const openShortcuts = useCallback(() => setShortcutsOpen(true), []);
  const openAchievements = useCallback(() => setAchievementsOpen(true), []);

  useKeyboardShortcuts({
    onHelp: openShortcuts,
    onFullscreen: isLab ? toggleFullscreen : undefined,
    onEscape: closeAll,
  });

  const value = useMemo(
    () => ({ openShortcuts, openAchievements, toggleFullscreen, isLab }),
    [openShortcuts, openAchievements, toggleFullscreen, isLab]
  );

  return (
    <AppUIContext.Provider value={value}>
      {children}
      <KeyboardShortcutsDialog
        open={shortcutsOpen}
        onClose={() => setShortcutsOpen(false)}
      />
      <AchievementsPanel
        open={achievementsOpen}
        onClose={() => setAchievementsOpen(false)}
      />
      <AchievementToast />
    </AppUIContext.Provider>
  );
}
