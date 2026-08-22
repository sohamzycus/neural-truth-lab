// ponytail: keep ids in sync with ASSIGNMENT_MINIMUM in chronology.ts
import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const root = dirname(fileURLToPath(import.meta.url));
const src = readFileSync(join(root, "chronology.ts"), "utf8");
const ids = [...src.matchAll(/id: "([^"]+)"/g)].map((m) => m[1]);

const minimum = {
  "scaled-dot-product": true,
  "multi-head-attention": true,
  "learned-positions": true,
  "sinusoidal-positions": true,
  rope: true,
  alibi: true,
  mqa: true,
  gqa: true,
  "sliding-window": true,
  "attention-sinks": true,
  "ntk-aware-scaling": true,
  yarn: true,
  "linear-attention": true,
  deltanet: true,
  "gated-deltanet": true,
  mla: true,
  "sparse-transformer": true,
  "topk-attention": true,
  nsa: true,
  csa: true,
  dsa: true,
  drope: true,
};

describe("chronology assignment coverage", () => {
  it("includes all minimum mechanism ids", () => {
    for (const id of Object.keys(minimum)) {
      assert.ok(ids.includes(id), `missing chronology entry: ${id}`);
    }
  });

  it("DroPE points to Sakana paper not wrong arxiv", () => {
    assert.match(src, /2512\.12167/);
    assert.doesNotMatch(src, /2503\.02658/);
  });

  it("top-k cites Explicit Sparse Transformer not Performers", () => {
    assert.match(src, /1912\.11637/);
    assert.doesNotMatch(src, /2009\.14794/);
  });
});
