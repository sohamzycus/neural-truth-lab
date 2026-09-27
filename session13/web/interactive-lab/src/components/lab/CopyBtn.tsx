import { useState } from "react";
import { copyText } from "../../lib/copy";

export function CopyBtn({ text }: { text: string }) {
  const [ok, setOk] = useState(false);
  return (
    <button
      type="button"
      className="rounded border border-white/20 px-2 py-1 text-xs hover:bg-white/10"
      onClick={async () => {
        const done = await copyText(text);
        setOk(done);
        setTimeout(() => setOk(false), 1500);
      }}
    >
      {ok ? "Copied" : "Copy"}
    </button>
  );
}
