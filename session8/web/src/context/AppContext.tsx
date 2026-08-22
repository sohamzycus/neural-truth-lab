import { createContext, useContext, useState, useCallback, type ReactNode } from "react";

type Mode = "beginner" | "expert";

interface AppContextValue {
  mode: Mode;
  toggleMode: () => void;
  activeChapter: number;
  setActiveChapter: (n: number) => void;
  activeEntryId: string | null;
  setActiveEntryId: (id: string | null) => void;
  showSixtySecond: boolean;
  setShowSixtySecond: (v: boolean) => void;
}

const AppContext = createContext<AppContextValue | null>(null);

export function AppProvider({ children }: { children: ReactNode }) {
  const [mode, setMode] = useState<Mode>("beginner");
  const [activeChapter, setActiveChapter] = useState(0);
  const [activeEntryId, setActiveEntryId] = useState<string | null>(null);
  const [showSixtySecond, setShowSixtySecond] = useState(false);

  const toggleMode = useCallback(() => {
    setMode((m) => (m === "beginner" ? "expert" : "beginner"));
  }, []);

  return (
    <AppContext.Provider
      value={{
        mode,
        toggleMode,
        activeChapter,
        setActiveChapter,
        activeEntryId,
        setActiveEntryId,
        showSixtySecond,
        setShowSixtySecond,
      }}
    >
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error("useApp must be used within AppProvider");
  return ctx;
}
