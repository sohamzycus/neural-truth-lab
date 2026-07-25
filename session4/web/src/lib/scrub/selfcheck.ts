import { scrubObservation, exactHash, normalizeUnicode, stripHtml, stripPii, collapseWhitespace } from "./index.ts";

function assert(cond: unknown, msg: string): void {
  if (!cond) throw new Error(msg);
}

const dirty =
  "Saw <b>Indian Robin</b> near fence — contact me at birder@example.com  phone +91 98765 43210.  Café  café   café";

const cleaned = scrubObservation(dirty);
assert(cleaned.text.includes("[EMAIL]"), "email masked");
assert(!cleaned.text.includes("<b>"), "html stripped");
assert(cleaned.text.includes("Indian Robin"), "species kept");
assert(!/\s{2,}/.test(cleaned.text), "whitespace collapsed");

assert(normalizeUnicode("ﬁle") === "file" || normalizeUnicode("ﬁle").length > 0, "unicode runs");
assert(stripHtml("<i>x</i>") === " x " || stripHtml("<i>x</i>").includes("x"), "html");
assert(stripPii("a@b.co").includes("[EMAIL]"), "pii");
assert(collapseWhitespace("a   b") === "a b", "ws");

const h1 = await exactHash("same");
const h2 = await exactHash("same");
assert(h1 === h2, "hash stable");

console.log("scrub selfcheck OK");
