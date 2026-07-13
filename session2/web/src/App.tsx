import { useEffect, useState } from "react";
import { HfBpeEncoder } from "./lib/hf-encoder";
import { loadJson } from "./types";
import type { VerifiedSubmission } from "./types";
import { VerifiedSubmissionPage, SectionLegacyResearch } from "./components/VerifiedSections";
import { SiteNav } from "./components/NarrativeSections";

const PRESETS = [
  "India's population is 1,428,627,663.",
  "India भारत భారతదేశం ভারত",
  "भारत एक विविध देश है।",
  "[India](https://en.wikipedia.org/wiki/India)",
];

export default function App() {
  const [verified, setVerified] = useState<VerifiedSubmission | null>(null);
  const [encoder, setEncoder] = useState<HfBpeEncoder | null>(null);
  const [playText, setPlayText] = useState(PRESETS[0]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      loadJson<VerifiedSubmission>("/data/verifiedSubmission.json"),
      HfBpeEncoder.load("/data/submission/tokenizer.json"),
    ])
      .then(([v, enc]) => {
        setVerified(v);
        setEncoder(enc);
      })
      .catch((e) => setError(String(e)));
  }, []);

  const tokens = encoder ? encoder.encodeTokens(playText) : [];
  const ids = encoder ? encoder.encodeIds(playText) : [];
  const rtOk = encoder ? encoder.verifyRoundtrip(playText) : false;

  return (
    <div className="min-h-screen pb-20">
      <SiteNav />
      {error && (
        <div className="bg-[var(--color-saffron)]/20 p-4 text-center text-sm" role="alert">
          Failed to load verified submission data. Run{" "}
          <code className="text-xs">python scripts/generate_verified_submission_data.py</code> ({error})
        </div>
      )}

      <VerifiedSubmissionPage data={verified} />
      <SectionLegacyResearch />

      <section className="mx-auto max-w-6xl px-4 py-14" id="playground">
        <h2 className="text-[clamp(2rem,4vw,3rem)] font-bold">Try the frozen tokenizer</h2>
        <p className="mt-2 text-sm text-[var(--color-ink)]/70">
          Loads <code className="text-xs">submission/tokenizer.json</code> — NFKC → Metaspace → BPE → Metaspace decode
          (parity-checked against <code className="text-xs">encoder.py</code>).
        </p>
        <div className="mt-4 flex flex-wrap gap-2">
          {PRESETS.map((p) => (
            <button key={p} type="button" className="btn text-xs" onClick={() => setPlayText(p)}>
              {p.slice(0, 36)}{p.length > 36 ? "…" : ""}
            </button>
          ))}
        </div>
        <textarea
          className="mt-4 w-full rounded border border-[var(--color-ink)]/15 bg-white/40 p-3 font-mono text-sm"
          rows={3}
          value={playText}
          onChange={(e) => setPlayText(e.target.value)}
          aria-label="Tokenizer input"
        />
        {encoder && (
          <div className="mt-4 font-mono text-xs">
            <div className="text-sm font-semibold font-sans">Tokens ({tokens.length})</div>
            <div className="mt-2 flex flex-wrap gap-1">{tokens.map((t, i) => <span key={i} className="rounded border px-1">{t}</span>)}</div>
            <div className="mt-2 text-[var(--color-ink)]/60">IDs: {ids.join(", ")}</div>
            <div className="mt-2">Round-trip: {rtOk ? "PASS" : "FAIL"} · Decoded: {encoder.decode(ids)}</div>
          </div>
        )}
      </section>

      <footer className="mx-auto max-w-6xl px-4 py-8 text-center text-xs text-[var(--color-ink)]/50">
        <p>
          Reproduce: <code>cd submission && python evaluate_tokenizer.py</code>
        </p>
      </footer>
    </div>
  );
}
