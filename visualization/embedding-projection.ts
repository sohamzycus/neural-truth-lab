export interface Point2D {
  token: string;
  tokenId: number;
  x: number;
  y: number;
}

function meanCenter(matrix: number[][]): number[][] {
  const d = matrix[0].length;
  const mean = Array(d).fill(0);
  for (const row of matrix) {
    for (let j = 0; j < d; j++) mean[j] += row[j];
  }
  for (let j = 0; j < d; j++) mean[j] /= matrix.length;
  return matrix.map((row) => row.map((v, j) => v - mean[j]));
}

function covariance(X: number[][]): number[][] {
  const n = X.length;
  const d = X[0].length;
  const C = Array.from({ length: d }, () => Array(d).fill(0));
  for (const row of X) {
    for (let i = 0; i < d; i++) {
      for (let j = 0; j < d; j++) {
        C[i][j] += row[i] * row[j];
      }
    }
  }
  const denom = Math.max(n - 1, 1);
  return C.map((row) => row.map((v) => v / denom));
}

function matVec(M: number[][], v: number[]): number[] {
  return M.map((row) => row.reduce((s, val, i) => s + val * v[i], 0));
}

function normalize(v: number[]): number[] {
  const n = Math.hypot(...v) || 1;
  return v.map((x) => x / n);
}

function powerEigenvector(M: number[][], iterations = 60): number[] {
  let v = normalize(Array(M.length).fill(0).map(() => Math.random()));
  for (let i = 0; i < iterations; i++) {
    v = normalize(matVec(M, v));
  }
  return v;
}

function deflate(M: number[][], vec: number[], eigenvalue: number): number[][] {
  return M.map((row, i) =>
    row.map((val, j) => val - eigenvalue * vec[i] * vec[j])
  );
}

function project(X: number[][], pc: number[]): number[] {
  return X.map((row) => row.reduce((s, v, i) => s + v * pc[i], 0));
}

/** PCA to 2D — ponytail: power iteration fine for vocab≤32, dim≤16 */
export function pca2D(
  embeddings: Float32Array,
  vocabSize: number,
  dim: number,
  idToToken: string[]
): Point2D[] {
  const rows: number[][] = [];
  for (let i = 0; i < vocabSize; i++) {
    if (idToToken[i] === "<pad>") continue;
    rows.push(Array.from(embeddings.slice(i * dim, (i + 1) * dim)));
  }

  if (rows.length < 2) {
    return idToToken
      .map((token, tokenId) => ({ token, tokenId, x: 0, y: 0 }))
      .filter((p) => p.token !== "<pad>");
  }

  const X = meanCenter(rows);
  let C = covariance(X);
  const pc1 = powerEigenvector(C);
  const eval1 = matVec(C, pc1).reduce((s, v, i) => s + v * pc1[i], 0);
  C = deflate(C, pc1, eval1);
  const pc2 = powerEigenvector(C);

  const coords1 = project(X, pc1);
  const coords2 = project(X, pc2);

  let idx = 0;
  return idToToken
    .map((token, tokenId) => {
      if (token === "<pad>") return null;
      const point = { token, tokenId, x: coords1[idx], y: coords2[idx] };
      idx++;
      return point;
    })
    .filter((p): p is Point2D => p !== null);
}

export function cosineSimilarity(a: number[], b: number[]): number {
  let dot = 0;
  let na = 0;
  let nb = 0;
  for (let i = 0; i < a.length; i++) {
    dot += a[i] * b[i];
    na += a[i] * a[i];
    nb += b[i] * b[i];
  }
  return dot / (Math.sqrt(na) * Math.sqrt(nb) || 1);
}

export function topNeighbors(
  embeddings: Float32Array,
  dim: number,
  tokenId: number,
  idToToken: string[],
  k = 3
): { token: string; similarity: number }[] {
  const vec = Array.from(embeddings.slice(tokenId * dim, (tokenId + 1) * dim));
  const scores: { token: string; similarity: number }[] = [];

  for (let i = 0; i < idToToken.length; i++) {
    if (i === tokenId || idToToken[i] === "<pad>") continue;
    const other = Array.from(embeddings.slice(i * dim, (i + 1) * dim));
    scores.push({
      token: idToToken[i],
      similarity: cosineSimilarity(vec, other),
    });
  }

  return scores.sort((a, b) => b.similarity - a.similarity).slice(0, k);
}
