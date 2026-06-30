export type TokenCategory = "animal" | "fruit" | "verb" | "other";

export interface SyntheticCorpus {
  vocab: string[];
  tokenToId: Record<string, number>;
  idToToken: string[];
  sequences: number[][];
  targets: number[];
  categories: Record<string, TokenCategory>;
  frequencies: Record<string, number>;
}

const ANIMALS = ["cat", "dog", "cow", "lion"] as const;
const FRUITS = ["apple", "banana", "mango", "orange"] as const;
const PAD = "<pad>";
const SEQ_LEN = 3;

function categorize(token: string): TokenCategory {
  if ((ANIMALS as readonly string[]).includes(token)) return "animal";
  if ((FRUITS as readonly string[]).includes(token)) return "fruit";
  if (
    ["eat", "eats", "run", "runs", "see", "sees", "chase", "chases"].includes(
      token
    )
  )
    return "verb";
  return "other";
}

export function buildSyntheticCorpus(): SyntheticCorpus {
  const nouns = [...ANIMALS, ...FRUITS];
  const sentences: string[] = [];

  for (const noun of nouns) {
    sentences.push(`The ${noun} eats`);
    sentences.push(`The ${noun} runs`);
    sentences.push(`The ${noun} sees`);
  }
  for (const noun of nouns) {
    sentences.push(`The lion chases the ${noun}`);
  }

  const frequencies: Record<string, number> = {};
  for (const sentence of sentences) {
    for (const t of sentence.toLowerCase().split(/\s+/)) {
      frequencies[t] = (frequencies[t] ?? 0) + 1;
    }
  }

  const vocab = [PAD, ...Object.keys(frequencies).sort()];
  const tokenToId = Object.fromEntries(vocab.map((t, i) => [t, i]));
  const idToToken = vocab;

  const sequences: number[][] = [];
  const targets: number[] = [];

  for (const sentence of sentences) {
    const tokens = sentence.toLowerCase().split(/\s+/);
    if (tokens.length > SEQ_LEN) {
      for (let i = SEQ_LEN; i < tokens.length; i++) {
        sequences.push(
          tokens.slice(i - SEQ_LEN, i).map((t) => tokenToId[t])
        );
        targets.push(tokenToId[tokens[i]]);
      }
    } else {
      const padded = [PAD, ...tokens].slice(-SEQ_LEN);
      while (padded.length < SEQ_LEN) padded.unshift(PAD);
      sequences.push(padded.map((t) => tokenToId[t]));
      targets.push(tokenToId[tokens[tokens.length - 1]]);
    }
  }

  const categories: Record<string, TokenCategory> = {};
  for (const token of vocab) {
    categories[token] = categorize(token);
  }

  return {
    vocab,
    tokenToId,
    idToToken,
    sequences,
    targets,
    categories,
    frequencies,
  };
}
