"use client";

import { useEffect } from "react";

interface ShortcutHandlers {
  onHelp?: () => void;
  onFullscreen?: () => void;
  onEscape?: () => void;
}

export function useKeyboardShortcuts(handlers: ShortcutHandlers): void {
  useEffect(() => {
    const onKeyDown = (e: KeyboardEvent): void => {
      const tag = (e.target as HTMLElement)?.tagName;
      const typing =
        tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT";

      if (e.key === "Escape") {
        handlers.onEscape?.();
        return;
      }

      if (typing) return;

      if (e.key === "?" || (e.key === "/" && e.shiftKey)) {
        e.preventDefault();
        handlers.onHelp?.();
      }
      if (e.key === "f" || e.key === "F") {
        handlers.onFullscreen?.();
      }
    };

    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [handlers]);
}
