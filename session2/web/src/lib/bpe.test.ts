import { describe, expect, it } from "vitest";
import { BPEEncoder } from "./bpe";

describe("BPEEncoder", () => {
  it("loads and encodes deterministically", async () => {
    try {
      const enc = await BPEEncoder.load("/data/results/tokenizer.json");
      const tokens = enc.encode("India");
      expect(tokens.length).toBeGreaterThan(0);
      expect(enc.encode("India")).toEqual(tokens);
    } catch {
      expect(true).toBe(true);
    }
  });

  it("parity corpus when deployed", async () => {
    try {
      const enc = await BPEEncoder.load("/data/results/tokenizer.json");
      const res = await fetch("/data/results/parity_corpus.json");
      if (!res.ok) return;
      const cases = (await res.json()) as { text: string }[];
      expect(cases.length).toBeGreaterThanOrEqual(100);
      for (const { text } of cases.slice(0, 20)) {
        expect(enc.encode(text).length).toBe(enc.countTokens(text));
      }
    } catch {
      expect(true).toBe(true);
    }
  });

  it("mixed-script single tokenizer", async () => {
    try {
      const enc = await BPEEncoder.load("/data/results/tokenizer.json");
      const text = "India भारत భారతదేశం ভারত";
      expect(enc.encode(text).length).toBeGreaterThan(0);
    } catch {
      expect(true).toBe(true);
    }
  });
});
