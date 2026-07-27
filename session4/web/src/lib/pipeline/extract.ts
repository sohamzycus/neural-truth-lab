/** Pull note body from simple checklist / app export wrappers. */
export function extractNoteBody(raw: string): { text: string; extracted: boolean } {
  const checklist = raw.match(/(?:note|comments?|description)\s*[:=]\s*(.+)/i);
  if (checklist?.[1]) return { text: checklist[1].trim(), extracted: true };
  if (raw.includes("<") && raw.includes(">")) {
    return { text: raw, extracted: false };
  }
  return { text: raw, extracted: false };
}
