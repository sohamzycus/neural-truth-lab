/**
 * Faithful HF BPE encoder: NFKC + Metaspace + BPE (matches tokenizers pipeline).
 */

const META = "▁";

export interface HfTokenizerJson {
  model: {
    vocab: Record<string, number>;
    merges: [string, string][];
    unk_token?: string;
  };
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
    return new HfBpeEncoder((await res.json()) as HfTokenizerJson);
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

  private metaspacePretokens(text: string): string[] {
    const norm = text.normalize("NFKC");
    if (!norm) return [];
    const parts = norm.split(" ");
    if (parts.length === 1) return parts;
    const out = [parts[0]];
    for (let i = 1; i < parts.length; i++) out.push(META + parts[i]);
    return out;
  }

  private encodeBpeTokens(text: string): string[] {
    const tokens: string[] = [];
    for (const pretok of this.metaspacePretokens(text)) tokens.push(...this.bpeWord(pretok));
    return tokens;
  }

  encodeTokens(text: string): string[] {
    const idToTok = new Map(Object.entries(this.vocab).map(([k, v]) => [v, k]));
    return this.encodeIds(text).map((id) => idToTok.get(id) ?? "<unk>");
  }

  encodeIds(text: string): number[] {
    return this.encodeBpeTokens(text).map((t) => this.vocab[t] ?? this.unkId);
  }

  decode(tokenIds: number[]): string {
    const idToTok = new Map(Object.entries(this.vocab).map(([k, v]) => [v, k]));
    const tokens = tokenIds.map((id) => {
      const tok = idToTok.get(id);
      if (!tok || tok === "<unk>") return "";
      return tok;
    });
    return tokens.join("").replaceAll(META, " ");
  }

  decodeTokens(tokens: string[]): string {
    return tokens.join("").replaceAll(META, " ");
  }

  visibleNfkc(text: string): string {
    return [...text.normalize("NFKC")].filter((c) => !/\s/.test(c)).join("");
  }

  verifyRoundtrip(text: string): boolean {
    const decoded = this.decode(this.encodeIds(text));
    return this.visibleNfkc(decoded) === this.visibleNfkc(text);
  }
}
