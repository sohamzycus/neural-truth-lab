"use client";

import { useCallback, useEffect, useState } from "react";

export function useFullscreen(targetId = "main"): {
  isFullscreen: boolean;
  toggle: () => void;
  exit: () => void;
} {
  const [isFullscreen, setIsFullscreen] = useState(false);

  useEffect(() => {
    const onChange = (): void => {
      setIsFullscreen(Boolean(document.fullscreenElement));
    };
    document.addEventListener("fullscreenchange", onChange);
    return () => document.removeEventListener("fullscreenchange", onChange);
  }, []);

  const exit = useCallback(() => {
    if (document.fullscreenElement) void document.exitFullscreen();
  }, []);

  const toggle = useCallback(() => {
    if (document.fullscreenElement) {
      exit();
      return;
    }
    const el = document.getElementById(targetId);
    if (el) void el.requestFullscreen();
  }, [exit, targetId]);

  return { isFullscreen, toggle, exit };
}
