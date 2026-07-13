import { useEffect, useState } from "react";
import { HfBpeEncoder } from "./lib/hf-encoder";
import { loadJson } from "./types";
import type { VerifiedSubmission } from "./types";
import { ResearchStory, SectionReproduce, SectionTryIt } from "./components/ResearchStory";
import { SiteNav } from "./components/SiteNav";

const MULTILINGUAL_DEFAULT = `India's population is 1,428,627,663.
भारत एक विशाल देश है।
భారతదేశం వైవిధ్యభరితమైన దేశం.
ভারত একটি বৈচিত্র্যময় দেশ।`;

export default function App() {
  const [verified, setVerified] = useState<VerifiedSubmission | null>(null);
  const [encoder, setEncoder] = useState<HfBpeEncoder | null>(null);
  const [playText, setPlayText] = useState(MULTILINGUAL_DEFAULT);
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

  return (
    <div className="min-h-screen pb-16">
      <SiteNav />
      {error && (
        <div className="bg-[var(--color-saffron)]/20 p-4 text-center text-sm" role="alert">
          Run <code className="text-xs">python scripts/generate_verified_submission_data.py</code> ({error})
        </div>
      )}
      <ResearchStory data={verified} />
      <SectionTryIt encoder={encoder} playText={playText} setPlayText={setPlayText} />
      <SectionReproduce data={verified} />
      <footer className="mx-auto max-w-6xl px-4 py-8 text-center text-xs text-[var(--color-ink)]/45">
        SamaBPE · session2 · Hugging Face BPE + multilingual weight search
      </footer>
    </div>
  );
}
