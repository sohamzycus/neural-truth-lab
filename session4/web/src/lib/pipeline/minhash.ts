/** Word-shingle MinHash + LSH banding for near-duplicate clusters. */

const HASH_PRIMES = [
  2147483647, 2147483629, 2147483587, 2147483579, 2147483549, 2147483543, 2147483497, 2147483477,
  2147483423, 2147483399, 2147483371, 2147483363, 2147483353, 2147483339, 2147483329, 2147483299,
  2147483283, 2147483273, 2147483269, 2147483259, 2147483249, 2147483239, 2147483229, 2147483219,
  2147483209, 2147483199, 2147483189, 2147483179, 2147483169, 2147483159, 2147483149, 2147483139,
];

function hashStr(s: string, prime: number): number {
  let h = 0;
  for (let i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) % prime;
  return h;
}

export function wordShingles(text: string, k = 3): Set<string> {
  const words = text.toLowerCase().split(/\s+/).filter(Boolean);
  const out = new Set<string>();
  if (words.length < k) {
    if (words.length) out.add(words.join(" "));
    return out;
  }
  for (let i = 0; i <= words.length - k; i++) out.add(words.slice(i, i + k).join(" "));
  return out;
}

export function minHashSignature(shingles: Set<string>, dims = 32): number[] {
  if (shingles.size === 0) return Array(dims).fill(0);
  return HASH_PRIMES.slice(0, dims).map((prime) => {
    let min = Infinity;
    for (const sh of shingles) {
      const h = hashStr(sh, prime);
      if (h < min) min = h;
    }
    return min === Infinity ? 0 : min;
  });
}

/** Estimated Jaccard from MinHash agreement (standard estimator). */
export function jaccardEstimate(a: number[], b: number[]): number {
  if (a.length !== b.length || a.length === 0) return 0;
  let match = 0;
  for (let i = 0; i < a.length; i++) if (a[i] === b[i]) match++;
  return match / a.length;
}

const NEAR_THRESHOLD = 0.82;
const BAND_SIZE = 4;

function lshKey(sig: number[], band: number): string {
  const start = band * BAND_SIZE;
  return sig.slice(start, start + BAND_SIZE).join(":");
}

export type NearDupCluster = { repId: string; memberIds: string[] };

/** LSH bucket + greedy cluster on shard-sized input. */
export function clusterNearDuplicates(
  items: { id: string; sig: number[] }[],
): { clusters: NearDupCluster[]; nearDupCount: number } {
  const buckets = new Map<string, string[]>();
  for (const item of items) {
    for (let band = 0; band < Math.floor(item.sig.length / BAND_SIZE); band++) {
      const key = lshKey(item.sig, band);
      const list = buckets.get(key) ?? [];
      list.push(item.id);
      buckets.set(key, list);
    }
  }

  const byId = new Map(items.map((i) => [i.id, i]));
  const assigned = new Set<string>();
  const clusters: NearDupCluster[] = [];

  for (const ids of buckets.values()) {
    if (ids.length < 2) continue;
    const unique = [...new Set(ids)].filter((id) => !assigned.has(id));
    if (unique.length < 2) continue;

    const repId = unique[0]!;
    const rep = byId.get(repId)!;
    const members = [repId];
    assigned.add(repId);

    for (let i = 1; i < unique.length; i++) {
      const id = unique[i]!;
      if (assigned.has(id)) continue;
      const other = byId.get(id)!;
      if (jaccardEstimate(rep.sig, other.sig) >= NEAR_THRESHOLD) {
        members.push(id);
        assigned.add(id);
      }
    }
    if (members.length > 1) clusters.push({ repId, memberIds: members });
  }

  const nearDupCount = clusters.reduce((n, c) => n + c.memberIds.length - 1, 0);
  return { clusters, nearDupCount };
}
