import { SITE } from "@/lib/constants";

export async function sharePage(url?: string): Promise<void> {
  const shareUrl =
    url ?? (typeof window !== "undefined" ? window.location.href : "");
  const payload = {
    title: SITE.name,
    text: SITE.tagline,
    url: shareUrl,
  };
  if (typeof navigator !== "undefined" && navigator.share) {
    try {
      await navigator.share(payload);
      return;
    } catch {
      // user cancelled or share failed — fall through to clipboard
    }
  }
  if (typeof navigator !== "undefined" && navigator.clipboard) {
    await navigator.clipboard.writeText(shareUrl);
  }
}
