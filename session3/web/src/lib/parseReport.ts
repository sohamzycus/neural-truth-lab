export type Chapter = { id: string; title: string; markdown: string };

export function parseChapters(reportMd: string): Chapter[] {
  const parts = reportMd.split(/^## /m).slice(1);
  return parts.map((part, i) => {
    const nl = part.indexOf("\n");
    const title = (nl === -1 ? part : part.slice(0, nl)).trim();
    const body = part.slice(nl + 1);
    const id = title.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "") || `ch-${i}`;
    return { id, title, markdown: `## ${title}\n\n${body}` };
  });
}
