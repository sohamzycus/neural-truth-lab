import { describe, it } from "node:test";
import assert from "node:assert/strict";

function softmax(arr) {
  const max = Math.max(...arr);
  const exps = arr.map((x) => Math.exp(x - max));
  const sum = exps.reduce((a, b) => a + b, 0);
  return exps.map((e) => e / sum);
}

function pairCount(n) {
  return n * n;
}

function kvCacheBytes(seqLen, layers, kvHeads, headDim, bytesPerElem = 2) {
  return seqLen * layers * kvHeads * headDim * 2 * bytesPerElem;
}

describe("math utilities", () => {
  it("softmax sums to 1", () => {
    const s = softmax([1, 2, 3]);
    const sum = s.reduce((a, b) => a + b, 0);
    assert.ok(Math.abs(sum - 1) < 1e-6);
  });

  it("pairCount is n²", () => {
    assert.equal(pairCount(128), 16384);
    assert.equal(pairCount(1024), 1048576);
  });

  it("kvCacheBytes scales with kv heads", () => {
    const mha = kvCacheBytes(100, 32, 8, 128);
    const mqa = kvCacheBytes(100, 32, 1, 128);
    assert.equal(mha / mqa, 8);
  });
});
