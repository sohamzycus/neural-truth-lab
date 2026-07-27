/** Strip orphan / unbalanced HTML-ish tags left after partial exports. */
export function cleanGhostTags(text: string): string {
  return text
    .replace(/<\/?[a-z][^>]*>/gi, (tag) => (tag.startsWith("</") ? " " : " "))
    .replace(/<<+|>>+/g, " ");
}
