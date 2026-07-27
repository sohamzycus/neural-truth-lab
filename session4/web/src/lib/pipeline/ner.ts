import gazetteer from "./data/ner_gazetteer.json";

export type NerEntityType = "EMAIL" | "PHONE" | "PERSON" | "LOC" | "ORG";

export type NerEntity = {
  type: NerEntityType;
  start: number;
  end: number;
  text: string;
};

type Span = NerEntity;

function findGazetteerSpans(text: string, terms: string[], type: NerEntityType): Span[] {
  const spans: Span[] = [];
  const lower = text.toLowerCase();
  for (const term of terms) {
    const t = term.toLowerCase();
    let idx = 0;
    while ((idx = lower.indexOf(t, idx)) !== -1) {
      const before = idx === 0 ? " " : lower[idx - 1]!;
      const after = lower[idx + t.length] ?? " ";
      const boundary = /[\s,.;:!?()[\]{}"']/.test(before) && /[\s,.;:!?()[\]{}"']/.test(after);
      if (boundary) {
        spans.push({ type, start: idx, end: idx + t.length, text: text.slice(idx, idx + t.length) });
      }
      idx += t.length;
    }
  }
  return spans;
}

function findRegexSpans(text: string, re: RegExp, type: NerEntityType): Span[] {
  const spans: Span[] = [];
  const r = new RegExp(re.source, re.flags.includes("g") ? re.flags : re.flags + "g");
  let m: RegExpExecArray | null;
  while ((m = r.exec(text))) {
    spans.push({ type, start: m.index, end: m.index + m[0].length, text: m[0] });
  }
  return spans;
}

/** Gazetteer + pattern NER (PERSON/LOC/ORG/EMAIL/PHONE) with overlap resolution. */
export function extractEntities(text: string): NerEntity[] {
  const spans: Span[] = [
    ...findRegexSpans(text, /[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/gi, "EMAIL"),
    ...findRegexSpans(text, /\+?\d[\d\s().-]{8,}\d/g, "PHONE"),
    ...findGazetteerSpans(text, gazetteer.persons, "PERSON"),
    ...findGazetteerSpans(text, gazetteer.locations, "LOC"),
    ...findGazetteerSpans(text, gazetteer.organizations, "ORG"),
    ...findRegexSpans(
      text,
      /\b[A-Z][a-z]+ [A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b(?=\s*(?:observed|saw|reported|noted|spotted))/g,
      "PERSON",
    ),
  ];

  spans.sort((a, b) => b.end - b.start - (a.end - a.start) || a.start - b.start);
  const kept: Span[] = [];
  for (const s of spans) {
    if (kept.some((k) => !(s.end <= k.start || s.start >= k.end))) continue;
    kept.push(s);
  }
  kept.sort((a, b) => b.start - a.start);
  return kept;
}

const MASK: Record<NerEntityType, string> = {
  EMAIL: "[EMAIL]",
  PHONE: "[PHONE]",
  PERSON: "[PERSON]",
  LOC: "[LOC]",
  ORG: "[ORG]",
};

export function maskNer(text: string): { text: string; entities: NerEntity[] } {
  const entities = extractEntities(text);
  let out = text;
  for (const e of entities) {
    out = out.slice(0, e.start) + MASK[e.type] + out.slice(e.end);
    const delta = MASK[e.type].length - (e.end - e.start);
    for (const other of entities) {
      if (other.start > e.start) {
        other.start += delta;
        other.end += delta;
      }
    }
  }
  return { text: out, entities };
}
