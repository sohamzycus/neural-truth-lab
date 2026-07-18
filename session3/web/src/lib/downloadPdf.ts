const PDF_CSS = `
  * { box-sizing: border-box; }
  body {
    font-family: "Manrope", system-ui, sans-serif;
    font-size: 10pt;
    line-height: 1.55;
    color: #1a1410;
  }
  h1 { font-size: 16pt; color: #2c3e6b; margin: 0 0 12pt; page-break-after: avoid; }
  h2 {
    font-size: 12pt;
    color: #2c3e6b;
    border-bottom: 2px solid #c45c26;
    padding-bottom: 4pt;
    margin: 14pt 0 8pt;
    page-break-after: avoid;
  }
  h3 { font-size: 10.5pt; margin: 10pt 0 6pt; page-break-after: avoid; }
  p, li { margin: 0 0 6pt; }
  table { width: 100%; border-collapse: collapse; font-size: 8pt; margin: 8pt 0; }
  th, td { border: 1px solid #ccc; padding: 4pt 6pt; text-align: left; }
  th { background: #ebe4d4; font-size: 7pt; text-transform: uppercase; }
  code, pre { font-family: "JetBrains Mono", monospace; font-size: 8pt; }
  pre {
    background: #f5f2ea;
    padding: 8pt;
    border-radius: 4pt;
    white-space: pre-wrap;
    word-break: break-word;
  }
  blockquote {
    margin: 8pt 0;
    padding: 6pt 10pt;
    border-left: 3px solid #c45c26;
    background: #faf8f3;
  }
  .pdf-chapter { page-break-before: always; }
  .pdf-chapter:first-child { page-break-before: avoid; }
  .pdf-cover {
    text-align: center;
    padding: 48pt 24pt;
    page-break-after: always;
  }
  .pdf-cover h1 { font-size: 22pt; border: none; }
  .pdf-cover p { color: #5c5c66; font-size: 11pt; }
`;

function parseTopLevelSections(md: string): { title: string; body: string }[] {
  const parts = md.split(/^# /m);
  return parts
    .map((part) => part.trim())
    .filter(Boolean)
    .map((part) => {
      const nl = part.indexOf("\n");
      const title = nl === -1 ? part : part.slice(0, nl).trim();
      const body = nl === -1 ? "" : part.slice(nl + 1).trim();
      return { title, body };
    });
}

function escapeHtml(s: string): string {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

export async function downloadReportPdf(markdown: string): Promise<void> {
  const [{ marked }, html2pdfModule] = await Promise.all([
    import("marked"),
    import("html2pdf.js"),
  ]);
  const html2pdf = html2pdfModule.default;
  marked.setOptions({ gfm: true });

  const sections = parseTopLevelSections(markdown);
  const cover = `
    <div class="pdf-cover">
      <h1>IndiaOne-40B</h1>
      <p>Internal Research Proposal · India-First Foundation Model</p>
      <p>Confidential · ${new Date().toISOString().slice(0, 10)}</p>
    </div>`;

  const chapters = sections
    .map(
      (s) =>
        `<section class="pdf-chapter"><h1>${escapeHtml(s.title)}</h1>${marked.parse(s.body)}</section>`,
    )
    .join("");

  const host = document.createElement("div");
  host.style.cssText = "position:fixed;left:-10000px;top:0;width:190mm;";
  host.innerHTML = `<style>${PDF_CSS}</style><div class="pdf-root">${cover}${chapters}</div>`;
  document.body.appendChild(host);

  const root = host.querySelector(".pdf-root") as HTMLElement;

  try {
    await html2pdf()
      .set({
        margin: [10, 10, 10, 10],
        filename: "IndiaOne-40B-Report.pdf",
        image: { type: "jpeg", quality: 0.92 },
        html2canvas: { scale: 1.5, useCORS: true, logging: false },
        jsPDF: { unit: "mm", format: "a4", orientation: "portrait" },
        pagebreak: { mode: ["css", "legacy"], before: ".pdf-chapter" },
      })
      .from(root)
      .save();
  } finally {
    document.body.removeChild(host);
  }
}
