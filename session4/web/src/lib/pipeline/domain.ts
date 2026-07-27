/** Bird-domain enrichments applied after generic scrub. */

const SYNONYMS: Record<string, string> = {
  "indian robin": "Copsychus fulicatus",
  "asian koel": "Eudynamys scolopaceus",
  "black drongo": "Dicrurus macrocercus",
};

export function applyDomainEnrichment(text: string): { text: string; steps: string[] } {
  const steps: string[] = [];
  let t = text;

  for (const [common, sci] of Object.entries(SYNONYMS)) {
    const re = new RegExp(`\\b${common}\\b`, "gi");
    if (re.test(t)) {
      t = t.replace(re, `${common} (${sci})`);
      steps.push(`Taxonomy: ${common} → ${sci}`);
      break;
    }
  }

  const masked = t.replace(/(\d{1,2}\.\d{4,})/g, (m) => `${m.slice(0, 4)}xx`);
  if (masked !== t) {
    steps.push("GPS: masked to reduced precision");
    t = masked;
  }

  const callNorm = t.replace(/che+e[\s-]*che+e+/gi, "chee-chee");
  if (callNorm !== t) {
    steps.push("Call: normalized onomatopoeia");
    t = callNorm;
  }

  const media = t.replace(/\/media\/\S+\.(wav|mp3|ogg)/gi, "[media-removed]");
  if (media !== t) {
    steps.push("Media: removed broken recording refs");
    t = media;
  }

  if (/\bconfirmed\b/i.test(t)) steps.push("Confidence: 1.0 (confirmed)");
  else if (/\blikely\b/i.test(t)) steps.push("Confidence: 0.7 (likely)");
  else if (/\bpossible\b/i.test(t)) steps.push("Confidence: 0.4 (possible)");

  return { text: t, steps };
}
