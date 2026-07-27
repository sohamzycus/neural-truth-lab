const MAX_CHARS = 4096;

/** Collapse runaway token/phrase repetition (e.g. "koel koel koel ×40"). */
export function collapseRepeats(text: string): { text: string; collapsed: boolean } {
  const words = text.split(/\s+/);
  if (words.length < 4) return { text, collapsed: false };
  const out: string[] = [];
  let i = 0;
  let collapsed = false;
  while (i < words.length) {
    let run = 1;
    while (i + run < words.length && words[i + run] === words[i]) run++;
    if (run >= 4) {
      out.push(words[i]!, `(×${run})`);
      collapsed = true;
      i += run;
    } else {
      for (let j = 0; j < run; j++) out.push(words[i + j]!);
      i += run;
    }
  }
  return { text: out.join(" "), collapsed };
}

export function capLength(text: string, max = MAX_CHARS): { text: string; truncated: boolean } {
  if (text.length <= max) return { text, truncated: false };
  return { text: text.slice(0, max) + "…", truncated: true };
}
