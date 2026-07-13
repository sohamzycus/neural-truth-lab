/**
 * Browser Hugging Face BPE encoder — mirrors tokenizers pipeline from tokenizer.json.
 */

export interface HfTokenizerJson {
  model: {
    vocab: Record<string, number>;
    merges: [string, string][];
    unk_token?: string;
  };
}

const WORDISH = /[^\p{L}\p{M}\p{N}]+/gu;

function normalize(text: string): string {
  return text.normalize("NFKC").replace(WORDISH, " ").trim();
}

function getPairs(symbols: string[]): Array<[string, string]> {
  const pairs: Array<[string, string]> = [];
  for (let i = 0; i < symbols.length - 1; i++) pairs.push([symbols[i], symbols[i + 1]]);
  return pairs;
}

function mergePair(symbols: string[], pair: [string, string]): string[] {
  const [a, b] = pair;
  const out: string[] = [];
  let i = 0;
  while (i < symbols.length) {
    if (i < symbols.length - 1 && symbols[i] === a && symbols[i + 1] === b) {
      out.push(a + b);
      i += 2;
    } else {
      out.push(symbols[i]);
      i += 1;
    }
  }
  return out;
}

export class HfBpeEncoder {
  private vocab: Record<string, number>;
  private mergeRanks: Map<string, number>;
  private unkId: number;

  constructor(data: HfTokenizerJson) {
    this.vocab = data.model.vocab;
    this.unkId = this.vocab[data.model.unk_token ?? "<unk>"] ?? 0;
    this.mergeRanks = new Map();
    data.model.merges.forEach(([a, b], i) => this.mergeRanks.set(`${a}|${b}`, i));
  }

  static async load(path = "/data/submission/tokenizer.json"): Promise<HfBpeEncoder> {
    const res = await fetch(path);
    const data = (await res.json()) as HfTokenizerJson;
    return new HfBpeEncoder(data);
  }

  private bpeWord(word: string): string[] {
    if (!word) return [];
    let symbols = [...word];
    if (symbols.length === 1) return symbols;
    while (symbols.length > 1) {
      const pairs = getPairs(symbols);
      let best: [string, string] | null = null;
      let bestRank = Infinity;
      for (const p of pairs) {
        const rank = this.mergeRanks.get(`${p[0]}|${p[1]}`);
        if (rank !== undefined && rank < bestRank) {
          bestRank = rank;
          best = p;
        }
      }
      if (!best) break;
      symbols = mergePair(symbols, best);
    }
    return symbols;
  }

  encodeTokens(text: string): string[] {
    const norm = normalize(text);
    if (!norm) return [];
    const words = norm.split(/\s+/).filter(Boolean);
    const tokens: string[] = [];
    for (const w of words) tokens.push(...this.bpeWord(w));
    return tokens;
  }

  encodeIds(text: string): number[] {
    return this.encodeTokens(text).map((t) => this.vocab[t] ?? this.unkId);
  }

  encode(text: string): string[] {
    return this.encodeTokens(text);
  }
}
