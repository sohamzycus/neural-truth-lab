export type Chapter = { id: string; num: string; shortTitle: string; title: string; markdown: string };

export function parseChapters(reportMd: string): Chapter[] {
  const chunks = reportMd.split(/^# /m).map((c) => c.trim()).filter(Boolean);
  const chapters = chunks.filter((c) => c.startsWith("§") || c.startsWith("Appendix") || c.startsWith("Closing"));

  return chapters.map((part, i) => {
    const nl = part.indexOf("\n");
    const title = (nl === -1 ? part : part.slice(0, nl)).trim();
    const body = nl === -1 ? "" : part.slice(nl + 1).trim();
    const numMatch = title.match(/^§(\d+)/);
    const num = numMatch ? numMatch[1] : title.startsWith("Appendix") ? "A" : title.startsWith("Closing") ? "C" : String(i);
    const shortTitle = numMatch ? `§${num}` : title.startsWith("Closing") ? "End" : "Appendix";
    const id =
      title
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, "-")
        .replace(/^-|-$/g, "") || `ch-${i}`;
    return {
      id,
      num,
      shortTitle,
      title,
      markdown: `# ${title}\n\n${body}`,
    };
  });
}
