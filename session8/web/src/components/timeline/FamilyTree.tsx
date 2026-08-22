import { FAMILY_TREE } from "../../data/chapters";

export function FamilyTree() {
  return (
    <section className="mt-20">
      <h2 className="text-2xl font-bold">Attention Family Tree</h2>
      <p className="mt-2 text-sm text-amber">
        This is a map after the story, not the story itself.
      </p>

      <div className="panel mt-6 p-8 text-center font-mono text-sm">
        <p className="text-lg font-bold text-cyan">{FAMILY_TREE.root}</p>
        <p className="my-4 text-muted">│</p>
        <div className="flex flex-wrap justify-center gap-8">
          {FAMILY_TREE.branches.map((b) => (
            <div key={b.name}>
              <p className="font-semibold text-violet">{b.name}</p>
              <p className="my-2 text-muted">│</p>
              <div className="flex flex-col gap-1">
                {b.children.map((c) => (
                  <span key={c} className="rounded bg-white/5 px-2 py-1 text-xs">{c}</span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
