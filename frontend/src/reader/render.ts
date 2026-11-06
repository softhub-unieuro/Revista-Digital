import {
  TextLayer,
  type PDFDocumentProxy,
  type RenderTask,
  type PDFPageProxy,
} from "pdfjs-dist";
export function renderPage(options: {
  pdf: PDFDocumentProxy;
  number: number;
  canvas: HTMLCanvasElement;
  text: HTMLDivElement | null;
  width: number;
  zoom: number;
  thumbnail: boolean;
}) {
  let cancelled = false;
  let loadedPage: PDFPageProxy | undefined;
  let task: RenderTask | undefined;
  let textLayer: TextLayer | undefined;
  const { pdf, number, canvas, text, width, zoom, thumbnail } = options;
  const started = performance.now();
  const done = (async () => {
    const page = (loadedPage = await pdf.getPage(number));
    if (cancelled) {
      page.cleanup();
      return;
    }
    const initial = page.getViewport({ scale: 1 });
    const viewport = page.getViewport({
      scale: ((width / initial.width) * zoom) / 100,
    });
    const ratio = Math.min(
      window.devicePixelRatio || 1,
      2,
      Math.sqrt(
        (thumbnail ? 40000 : 4000000) / (viewport.width * viewport.height),
      ),
    );
    canvas.width = Math.max(1, Math.floor(viewport.width * ratio));
    canvas.height = Math.max(1, Math.floor(viewport.height * ratio));
    canvas.style.width = `${viewport.width}px`;
    canvas.style.height = `${viewport.height}px`;
    const parent = canvas.parentElement!;
    parent.style.setProperty("--scale-factor", String(viewport.scale));
    parent.style.setProperty("--total-scale-factor", String(viewport.scale));
    parent.style.setProperty("--user-unit", "1");
    parent.style.setProperty("--min-font-size", "1");
    task = page.render({
      canvas,
      viewport,
      transform: ratio === 1 ? undefined : [ratio, 0, 0, ratio, 0, 0],
      background: "#fff",
    });
    await task.promise;
    if (text && !cancelled) {
      textLayer = new TextLayer({
        textContentSource: await page.getTextContent(),
        container: text,
        viewport,
      });
      if (cancelled) return;
      await textLayer.render();
    }
    canvas.dataset.renderMs = String(Math.round(performance.now() - started));
    page.cleanup();
  })();
  return {
    done,
    cancel() {
      cancelled = true;
      task?.cancel();
      textLayer?.cancel();
      void done
        .catch(() => {})
        .finally(() => {
          canvas.width = 0;
          canvas.height = 0;
          text?.replaceChildren();
          loadedPage?.cleanup();
        });
    },
  };
}
