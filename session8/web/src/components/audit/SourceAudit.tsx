import { CHRONOLOGY } from "../../data/chronology";

export function SourceAudit() {
  return (
    <section id="source-audit" className="scroll-mt-20 mt-20">
      <h2 className="text-2xl font-bold">Source Audit</h2>
      <p className="mt-2 text-muted">
        Every mechanism traced to a primary source. Community techniques are labeled explicitly.
      </p>

      <div className="mt-6 overflow-x-auto">
        <table className="w-full min-w-[720px] text-left text-sm">
          <thead>
            <tr className="border-b border-white/10 text-xs uppercase text-muted">
              <th className="py-3 pr-4">Date</th>
              <th className="py-3 pr-4">Mechanism</th>
              <th className="py-3 pr-4">Authors</th>
              <th className="py-3 pr-4">Venue</th>
              <th className="py-3 pr-4">Type</th>
              <th className="py-3">Link</th>
            </tr>
          </thead>
          <tbody>
            {CHRONOLOGY.map((e) => (
              <tr key={e.id} className="border-b border-white/5 hover:bg-white/[0.02]">
                <td className="py-3 pr-4 font-mono text-xs">{e.date}</td>
                <td className="py-3 pr-4 font-medium">{e.title}</td>
                <td className="py-3 pr-4 text-muted">{e.authors}</td>
                <td className="py-3 pr-4 text-muted">{e.venue}</td>
                <td className="py-3 pr-4">
                  <span className={`rounded px-2 py-0.5 text-[10px] ${
                    e.sourceType === "COMMUNITY ORIGIN" ? "bg-amber/20 text-amber" : "bg-white/5 text-muted"
                  }`}>
                    {e.sourceType}
                  </span>
                </td>
                <td className="py-3">
                  <a href={e.sourceUrl} target="_blank" rel="noopener noreferrer" className="text-cyan hover:underline">
                    Source
                  </a>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
