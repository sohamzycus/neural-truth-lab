import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";

export type ManifestEntry = { path: string; sha256: string; bytes: number; records?: number };

export function sha256File(path: string, records?: number): ManifestEntry {
  const buf = readFileSync(path);
  return {
    path,
    sha256: createHash("sha256").update(buf).digest("hex"),
    bytes: buf.length,
    records,
  };
}

export function sha256Text(name: string, content: string, records?: number): ManifestEntry {
  const buf = Buffer.from(content, "utf8");
  return {
    path: name,
    sha256: createHash("sha256").update(buf).digest("hex"),
    bytes: buf.length,
    records,
  };
}
