import { motion } from "framer-motion";
import type { Discovery } from "../../types";
import { Section } from "../shell/AppShell";
import { InsightTile } from "../ui";

export function DiscoveriesSection({ items }: { items: Discovery[] }) {
  return (
    <Section
      id="discoveries"
      eyebrow="Corpus insights"
      title="Interesting Discoveries"
      subtitle="Browse corpus curiosities from 47M+ observations. Hover a tile for why it matters."
    >
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {items.map((d, i) => (
          <motion.div
            key={d.id}
            initial={{ opacity: 0, scale: 0.96 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true, margin: "-20px" }}
            transition={{ delay: (i % 3) * 0.06 }}
          >
            <InsightTile label={d.label} value={d.value} detail={d.detail} why={d.why} />
          </motion.div>
        ))}
      </div>
    </Section>
  );
}
