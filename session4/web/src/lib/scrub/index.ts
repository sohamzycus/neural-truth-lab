export function normalizeUnicode(text: string): string {
  return text.normalize("NFKC");
}

export function stripHtml(text: string): string {
  return text
    .replace(/<script[\s\S]*?>[\s\S]*?<\/script>/gi, " ")
    .replace(/<style[\s\S]*?>[\s\S]*?<\/style>/gi, " ")
    .replace(/<[^>]+>/g, " ")
    .replace(/&nbsp;/gi, " ")
    .replace(/&amp;/gi, "&")
    .replace(/&lt;/gi, "<")
    .replace(/&gt;/gi, ">")
    .replace(/&quot;/gi, '"');
}

export function stripPii(text: string): string {
  return text
    .replace(/[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/gi, "[EMAIL]")
    .replace(/\+?\d[\d\s().-]{8,}\d/g, "[PHONE]")
    .replace(/\b[A-Z][a-z]+ [A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b(?=\s*(?:observed|saw|reported))/g, "[OBSERVER]");
}

export function collapseWhitespace(text: string): string {
  return text.replace(/\s+/g, " ").trim();
}

export async function exactHash(text: string): Promise<string> {
  const data = new TextEncoder().encode(text);
  if (typeof crypto !== "undefined" && crypto.subtle) {
    const digest = await crypto.subtle.digest("SHA-256", data);
    return [...new Uint8Array(digest)]
      .map((b) => b.toString(16).padStart(2, "0"))
      .join("");
  }
  // Node fallback for selfcheck
  let h = 0;
  for (let i = 0; i < text.length; i++) h = (Math.imul(31, h) + text.charCodeAt(i)) | 0;
  return `fallback-${h}`;
}

export type ScrubResult = {
  text: string;
  steps: { name: string; detail: string }[];
};

export function scrubObservation(raw: string): ScrubResult {
  const steps: ScrubResult["steps"] = [];
  let text = raw;

  const afterUnicode = normalizeUnicode(text);
  if (afterUnicode !== text) steps.push({ name: "Unicode NFKC", detail: "Normalized compatibility characters" });
  text = afterUnicode;

  const afterHtml = stripHtml(text);
  if (afterHtml !== text) steps.push({ name: "HTML strip", detail: "Removed markup and entities" });
  text = afterHtml;

  const afterPii = stripPii(text);
  if (afterPii !== text) steps.push({ name: "PII removal", detail: "Masked emails, phones, observer names" });
  text = afterPii;

  const afterWs = collapseWhitespace(text);
  if (afterWs !== text) steps.push({ name: "Whitespace", detail: "Collapsed runs and trimmed" });
  text = afterWs;

  if (steps.length === 0) steps.push({ name: "Pass-through", detail: "No transforms triggered" });
  return { text, steps };
}
