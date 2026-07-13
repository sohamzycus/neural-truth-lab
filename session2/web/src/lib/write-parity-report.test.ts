import { describe, it, beforeAll } from "vitest";
import { readFileSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";
import { HfBpeEncoder } from "./hf-encoder";

const ROOT = resolve(__dirname, "../../..");
const GATE_CASES = resolve(ROOT, "results/gate-playground-cases.json");
const BROWSER_OUT = resolve(ROOT, "results/browser-parity-report.json");

interface GateCase {
  text: string;
  tokens: string[];
  ids: number[];
}

describe("write parity report for submission gate", () => {
  let encoder: HfBpeEncoder;
  let cases: GateCase[];

  beforeAll(async () => {
    const tokPath = resolve(__dirname, "../../public/data/submission/tokenizer.json");
    encoder = new HfBpeEncoder(JSON.parse(readFileSync(tokPath, "utf-8")));
    const src = GATE_CASES;
    const data = JSON.parse(readFileSync(src, "utf-8"));
    cases = data.cases;
  });

  it("writes browser parity report JSON", () => {
    const report = {
      generated_at: new Date().toISOString(),
      cases: cases.map((c) => {
        const ids = encoder.encodeIds(c.text);
        const tokens = encoder.encodeTokens(c.text);
        const decoded = encoder.decode(ids);
        return {
          input: c.text,
          ids,
          tokens,
          decoded,
          ids_match_python_fixture: JSON.stringify(ids) === JSON.stringify(c.ids),
        };
      }),
    };
    writeFileSync(BROWSER_OUT, JSON.stringify(report, null, 2), "utf-8");
  });
});
