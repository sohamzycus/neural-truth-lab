import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { CorpusStats } from "../../types";
import { Section } from "../shell/AppShell";

const PIE_COLORS = ["#5ec9a8", "#7eb8ff", "#e8b86d", "#6fbf8a", "#93a39a", "#d4a574", "#5c8f7a", "#7a9eb8"];

export function StatsSection({ stats }: { stats: CorpusStats }) {
  return (
    <Section
      id="stats"
      eyebrow="Ship readiness"
      title="Final Corpus Statistics"
      subtitle="Language mix, species distribution, quality climb, deduplication savings, and readiness."
    >
      <div className="grid gap-4 lg:grid-cols-2">
        <div className="panel p-5">
          <h3 className="mb-4 text-sm font-medium text-[var(--color-muted)]">Language distribution</h3>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={stats.languages} dataKey="value" nameKey="name" innerRadius={48} outerRadius={80} paddingAngle={2}>
                  {stats.languages.map((_, i) => (
                    <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} stroke="transparent" />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ background: "#121214", border: "1px solid rgba(255,255,255,0.08)", borderRadius: 8 }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div className="panel p-5">
          <h3 className="mb-4 text-sm font-medium text-[var(--color-muted)]">Species distribution</h3>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={stats.species}>
                <CartesianGrid stroke="rgba(255,255,255,0.06)" vertical={false} />
                <XAxis dataKey="name" tick={{ fill: "#8a8a93", fontSize: 10 }} interval={0} angle={-25} textAnchor="end" height={60} />
                <YAxis tick={{ fill: "#8a8a93", fontSize: 11 }} />
                <Tooltip
                  contentStyle={{ background: "#121214", border: "1px solid rgba(255,255,255,0.08)", borderRadius: 8 }}
                />
                <Bar dataKey="value" fill="#5ec9a8" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div className="panel p-5">
          <h3 className="mb-4 text-sm font-medium text-[var(--color-muted)]">Quality improvement</h3>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={stats.qualityTimeline}>
                <CartesianGrid stroke="rgba(255,255,255,0.06)" />
                <XAxis dataKey="stage" tick={{ fill: "#8a8a93", fontSize: 10 }} />
                <YAxis domain={[0, 1]} tick={{ fill: "#8a8a93", fontSize: 11 }} />
                <Tooltip
                  contentStyle={{ background: "#121214", border: "1px solid rgba(255,255,255,0.08)", borderRadius: 8 }}
                />
                <Line type="monotone" dataKey="score" stroke="#5ec9a8" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div className="panel p-5">
          <h3 className="mb-4 text-sm font-medium text-[var(--color-muted)]">Deduplication savings</h3>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={stats.dedupeSavings}>
                <CartesianGrid stroke="rgba(255,255,255,0.06)" vertical={false} />
                <XAxis dataKey="label" tick={{ fill: "#8a8a93", fontSize: 11 }} />
                <YAxis tick={{ fill: "#8a8a93", fontSize: 11 }} />
                <Tooltip
                  contentStyle={{ background: "#121214", border: "1px solid rgba(255,255,255,0.08)", borderRadius: 8 }}
                />
                <Bar dataKey="before" fill="#93a39a" radius={[4, 4, 0, 0]} />
                <Bar dataKey="after" fill="#5ec9a8" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
      <div className="mt-4 grid gap-4 sm:grid-cols-2">
        <div className="panel flex items-center justify-between p-6">
          <div>
            <div className="text-[11px] uppercase tracking-[0.16em] text-[var(--color-muted)]">Corpus readiness</div>
            <div className="mt-2 font-mono text-4xl text-[var(--color-accent)]">
              {(stats.readinessScore * 100).toFixed(0)}
            </div>
          </div>
          <div className="h-20 w-20 rounded-full border-4 border-[var(--color-accent)]/30 border-t-[var(--color-accent)]" />
        </div>
        <div className="panel p-6">
          <div className="text-[11px] uppercase tracking-[0.16em] text-[var(--color-muted)]">Avg token reduction</div>
          <div className="mt-2 font-mono text-4xl text-[var(--color-ok)]">{stats.tokenReductionPct}%</div>
          <p className="mt-2 text-sm text-[var(--color-muted)]">After dedupe, PII strip, and boilerplate removal.</p>
        </div>
      </div>
    </Section>
  );
}
