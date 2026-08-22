import { createContext, useContext, useState, useCallback, useEffect, type ReactNode } from "react";

type Mode = "beginner" | "expert";
type Theme = "light" | "dark" | "system";

interface AppContextValue {
  mode: Mode;
  toggleMode: () => void;
  theme: Theme;
  setTheme: (t: Theme) => void;
  resolvedTheme: "light" | "dark";
  activeChapter: number;
  setActiveChapter: (n: number) => void;
  activeEntryId: string | null;
  setActiveEntryId: (id: string | null) => void;
  showSixtySecond: boolean;
  setShowSixtySecond: (v: boolean) => void;
}

const AppContext = createContext<AppContextValue | null>(null);

function resolveTheme(theme: Theme): "light" | "dark" {
  if (theme === "system") {
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }
  return theme;
}

export function AppProvider({ children }: { children: ReactNode }) {
  const [mode, setMode] = useState<Mode>("beginner");
  const [theme, setThemeState] = useState<Theme>(() => {
    try {
      return (localStorage.getItem("attention-theme") as Theme) || "light";
    } catch {
      return "light";
    }
  });
  const [resolvedTheme, setResolvedTheme] = useState<"light" | "dark">("light");
  const [activeChapter, setActiveChapter] = useState(0);
  const [activeEntryId, setActiveEntryId] = useState<string | null>(null);
  const [showSixtySecond, setShowSixtySecond] = useState(false);

  const setTheme = useCallback((t: Theme) => {
    setThemeState(t);
    try {
      localStorage.setItem("attention-theme", t);
    } catch {
      /* ponytail: localStorage optional */
    }
  }, []);

  useEffect(() => {
    const apply = () => {
      const resolved = resolveTheme(theme);
      setResolvedTheme(resolved);
      document.documentElement.dataset.theme = resolved;
      document.querySelector('meta[name="theme-color"]')?.setAttribute(
        "content",
        resolved === "light" ? "#f4f6fb" : "#06080f",
      );
    };
    apply();
    if (theme !== "system") return;
    const mq = window.matchMedia("(prefers-color-scheme: dark)");
    mq.addEventListener("change", apply);
    return () => mq.removeEventListener("change", apply);
  }, [theme]);

  const toggleMode = useCallback(() => {
    setMode((m) => (m === "beginner" ? "expert" : "beginner"));
  }, []);

  return (
    <AppContext.Provider
      value={{
        mode,
        toggleMode,
        theme,
        setTheme,
        resolvedTheme,
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
