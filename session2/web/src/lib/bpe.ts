/**
 * Browser BPE encoder — must match Python samabpe.bpe.BPETokenizer
 */

import type { TokenizerData } from "../types";

const END_OF_WORD = "</w>";

export class BPEEncoder {
  private vocab: Record<string, number>;
  private mergeRanks: Map<string, number>;
  private pretokenization: TokenizerData["pretokenization"];
  private unkId: number;

  constructor(data: TokenizerData) {
    this.vocab = data.vocab;
    this.pretokenization = data.pretokenization;
    this.unkId = data.special_tokens["<unk>"] ?? 0;
    this.mergeRanks = new Map();
    data.merges.forEach((m: string[], i: number) => this.mergeRanks.set(`${m[0]}|${m[1]}`, i));
  }

  static async load(path = "/data/results/tokenizer.json"): Promise<BPEEncoder> {
    const res = await fetch(path);
    const data = (await res.json()) as TokenizerData;
    return new BPEEncoder(data);
  }

  private pretokenize(text: string): string[] {
    const nfc = text.normalize("NFC");
    if (this.pretokenization === "whitespace") {
      return nfc.split(/\s+/).filter(Boolean).map((w) => w + END_OF_WORD);
    }
    if (this.pretokenization === "character") return [...nfc];
    // grapheme — ponytail: use Intl.Segmenter when available
    if (typeof Intl !== "undefined" && "Segmenter" in Intl) {
      const seg = new Intl.Segmenter(undefined, { granularity: "grapheme" });
      return [...seg.segment(nfc)].map((s) => s.segment);
    }
    return [...nfc];
  }

  private wordToSymbols(word: string): string[] {
    if (this.pretokenization === "whitespace") {
      if (word.endsWith(END_OF_WORD)) {
        const core = word.slice(0, -END_OF_WORD.length);
        return [...core, END_OF_WORD];
      }
      return [...word];
    }
    return [...word];
  }

  private getPairs(symbols: string[]): Array<[string, string]> {
    const pairs: Array<[string, string]> = [];
    for (let i = 0; i < symbols.length - 1; i++) pairs.push([symbols[i], symbols[i + 1]]);
    return pairs;
  }

  private mergePair(symbols: string[], pair: [string, string]): string[] {
    const [first, second] = pair;
    const out: string[] = [];
    let i = 0;
    while (i < symbols.length) {
      if (i < symbols.length - 1 && symbols[i] === first && symbols[i + 1] === second) {
        out.push(first + second);
        i += 2;
      } else {
        out.push(symbols[i]);
        i++;
      }
    }
    return out;
  }

  private applyMerges(symbols: string[]): string[] {
    let pairs = this.getPairs(symbols);
    while (pairs.length > 0) {
      let best: [string, string] | null = null;
      let bestRank = Infinity;
      for (const p of pairs) {
        const rank = this.mergeRanks.get(`${p[0]}|${p[1]}`);
        if (rank !== undefined && rank < bestRank) {
          bestRank = rank;
          best = p;
        }
      }
      if (best === null) break;
      symbols = this.mergePair(symbols, best);
      pairs = this.getPairs(symbols);
    }
    return symbols;
  }

  encode(text: string): string[] {
    const out: string[] = [];
    for (const pt of this.pretokenize(text)) {
      out.push(...this.applyMerges(this.wordToSymbols(pt)));
    }
    return out;
  }

  encodeIds(text: string): number[] {
    return this.encode(text).map((t) => this.vocab[t] ?? this.unkId);
  }

  countTokens(text: string): number {
    return this.encode(text).length;
  }

  getVocabEntries(): Array<{ token: string; id: number }> {
    return Object.entries(this.vocab)
      .map(([token, id]) => ({ token, id }))
      .sort((a, b) => a.id - b.id);
  }
}

export function codePoints(token: string): string[] {
  return [...token].map((c) => `U+${c.codePointAt(0)!.toString(16).toUpperCase().padStart(4, "0")}`);
}

export function detectScript(char: string): string {
  const cp = char.codePointAt(0)!;
  if (cp < 128) return "latin";
  if (cp >= 0x0900 && cp <= 0x097f) return "devanagari";
  if (cp >= 0x0980 && cp <= 0x09ff) return "bengali";
  if (cp >= 0x0c00 && cp <= 0x0c7f) return "telugu";
  return "other";
}

export function graphemeCount(token: string): number {
  if (typeof Intl !== "undefined" && "Segmenter" in Intl) {
    const seg = new Intl.Segmenter(undefined, { granularity: "grapheme" });
    return [...seg.segment(token)].length;
  }
  return [...token].length;
}

export function scriptAttribution(token: string): string {
  const scripts = new Set(
    [...token].filter((c) => !/\s/.test(c)).map(detectScript)
  );
  if (scripts.size === 0) return "neutral";
  if (scripts.size === 1) return [...scripts][0];
  return "mixed";
}
