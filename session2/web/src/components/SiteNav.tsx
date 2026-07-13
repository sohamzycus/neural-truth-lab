export function SiteNav() {
  const links = [
    ["#overview", "Overview"],
    ["#how-it-works", "How SamaBPE Works"],
    ["#results", "Results"],
    ["#try-it", "Try It"],
    ["#reproduce", "Reproduce"],
    ["#methodology", "Methodology"],
  ];
  return (
    <nav className="sticky top-0 z-20 border-b border-[var(--color-ink)]/10 bg-[var(--color-paper)]/95 backdrop-blur-sm">
      <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-2 px-4 py-3 text-sm">
        <a href="#overview" className="font-bold text-[var(--color-indigo)]">SamaBPE</a>
        <div className="flex flex-wrap gap-3">
          {links.map(([href, label]) => (
            <a key={href} href={href} className="text-[var(--color-ink)]/70 hover:text-[var(--color-indigo)]">
              {label}
            </a>
          ))}
          <a href="https://github.com/sohamzycus/neural-truth-lab/tree/main/session2" className="text-[var(--color-ink)]/70 hover:text-[var(--color-indigo)]">
            GitHub
          </a>
        </div>
      </div>
    </nav>
  );
}
