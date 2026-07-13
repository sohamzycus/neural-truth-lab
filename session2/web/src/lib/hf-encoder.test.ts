import { describe, expect, it, beforeAll } from "vitest";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { HfBpeEncoder } from "./hf-encoder";

interface ParityCase {
  text: string;
  tokens: string[];
  ids: number[];
  count: number;
}

describe("HfBpeEncoder playground parity", () => {
  let encoder: HfBpeEncoder;
  let cases: ParityCase[];

  beforeAll(async () => {
    const tokPath = resolve(__dirname, "../../public/data/submission/tokenizer.json");
    const raw = readFileSync(tokPath, "utf-8");
    encoder = new HfBpeEncoder(JSON.parse(raw));
    const parityPath = resolve(__dirname, "../../public/data/playground_parity.json");
    cases = JSON.parse(readFileSync(parityPath, "utf-8")).cases;
  });

  it("has at least 20 multilingual parity cases", () => {
    expect(cases.length).toBeGreaterThanOrEqual(20);
  });

  for (const label of ["English", "Hindi", "Telugu", "Bengali", "mixed", "punctuation", "URL", "numbers"]) {
    it(`matches authoritative encoder (${label} cases)`, () => {
      // all cases checked each iteration — vitest runs one it block per category label for reporting
      for (const c of cases) {
        const tokens = encoder.encodeTokens(c.text);
        const ids = encoder.encodeIds(c.text);
        expect(tokens).toEqual(c.tokens);
        expect(ids).toEqual(c.ids);
        expect(ids.length).toBe(c.count);
      }
    });
  }
});
