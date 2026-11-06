export function clampPage(value: number, total: number): number {
  return Math.min(
    total,
    Math.max(1, Number.isFinite(value) ? Math.trunc(value) : 1),
  );
}
export function visiblePages(
  page: number,
  total: number,
  double: boolean,
): number[] {
  const n = clampPage(page, total);
  if (!double || n === 1) return [n];
  const first = n % 2 ? n - 1 : n;
  return first + 1 <= total ? [first, first + 1] : [first];
}
export function stepPage(
  page: number,
  total: number,
  double: boolean,
  direction: number,
): number {
  const pages = visiblePages(page, total, double);
  return clampPage(direction > 0 ? pages.at(-1)! + 1 : pages[0] - 1, total);
}
export function fittedPageWidth(
  viewportWidth: number,
  viewportHeight: number,
  pageCount: number,
  ratio: number,
  gap = 2,
): number {
  const columns = Math.max(1, Math.trunc(pageCount));
  const availableWidth = Math.max(
    1,
    viewportWidth - 32 - (columns - 1) * gap,
  );
  const availableHeight = Math.max(1, viewportHeight - 32);
  const pageRatio = Number.isFinite(ratio) && ratio > 0 ? ratio : 0.707;
  return Math.max(
    1,
    Math.min(availableWidth / columns, availableHeight * pageRatio),
  );
}
export function defaultDoublePage(isMobile: boolean): boolean {
  return !isMobile;
}
export function thumbnailWindow(scrollTop: number, total: number): number[] {
  const first = Math.max(0, Math.floor(scrollTop / 112) - 1) * 2 + 1;
  return Array.from(
    { length: Math.min(10, total - first + 1) },
    (_, i) => first + i,
  );
}
