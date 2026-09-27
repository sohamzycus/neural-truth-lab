
export type Precision = "float32" | "bfloat16";
export function paramEstimate(vocab: number, layers: number, hidden: number, seq: number, tie: boolean) {
  const emb = vocab * hidden + seq * hidden;
  const perLayer = 12 * hidden * hidden + 4 * hidden;
  const head = tie ? 0 : vocab * hidden;
  return emb + layers * perLayer + 2 * hidden + head;
}
export function memoryEstimate(params: number, batch: number, seq: number, hidden: number, layers: number, reversible: boolean, dtypeBytes = 4) {
  const weights = params * dtypeBytes;
  const grads = weights;
  const optim = weights * 2;
  const act = reversible ? batch * seq * hidden * dtypeBytes * layers * 0.35 : batch * seq * hidden * dtypeBytes * layers * 3;
  return { weights, grads, optim, activations: act, other: 128e6, total: weights + grads + optim + act + 128e6 };
}
export function fitStatus(total: number, gpuMemGb: number) {
  const lim = gpuMemGb * 1e9 * 0.9;
  if (total > lim) return "oom" as const;
  if (total > lim * 0.85) return "close" as const;
  return "fits" as const;
}
