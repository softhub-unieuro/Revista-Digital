import { useCallback, useEffect, useRef, useState } from "react";
import { Link, useParams, useSearchParams } from "react-router-dom";
import { useReducedMotion } from "motion/react";
import { getDocument, GlobalWorkerOptions, Util } from "pdfjs-dist";
import workerUrl from "pdfjs-dist/build/pdf.worker.min.mjs?url";
import "./text-layer.css";
import { request } from "../api";
import { editionFromApi } from "../catalog";
import { Brand, Cover, Icon } from "../ui";
import { renderPage } from "./render";
import { readerError } from "./errors";
import { PageTurn } from "./PageTurn";
import {
  clampPage,
  defaultDoublePage,
  fittedPageWidth,
  stepPage,
  thumbnailWindow,
  visiblePages,
} from "./model";
GlobalWorkerOptions.workerSrc = workerUrl;

function PdfPage({
  pdf,
  number,
  width,
  zoom = 100,
  thumbnail = false,
  go,
  retry,
}) {
  const raster = useRef(null);
  const [state, setState] = useState("loading"),
    [links, setLinks] = useState([]);
  useEffect(() => {
    let active = true;
    // StrictMode and zoom changes each receive a separate canvas. An old render
    // can finish cancellation without clearing the surface of its successor.
    const canvas = document.createElement("canvas");
    canvas.dataset.testid = thumbnail ? "pdf-thumbnail" : "pdf-page";
    canvas.setAttribute("aria-label", `Página ${number}`);
    const text = document.createElement("div");
    text.className = "textLayer";
    raster.current.replaceChildren(canvas, ...(thumbnail ? [] : [text]));
    const render = renderPage({
      pdf,
      number,
      width,
      zoom,
      thumbnail,
      canvas,
      text: thumbnail ? null : text,
    });
    render.done
      .then(async () => {
        if (!active) return;
        setState("ready");
        if (!thumbnail) {
          const page = await pdf.getPage(number);
          const original = page.getViewport({ scale: 1 });
          const viewport = page.getViewport({
            scale: ((width / original.width) * zoom) / 100,
          });
          const annotations = await page.getAnnotations();
          if (active)
            setLinks(
              annotations
                .filter((a) => a.subtype === "Link")
                .map((a) => {
                  const rect = Util.normalizeRect([
                    ...viewport.convertToViewportPoint(a.rect[0], a.rect[1]),
                    ...viewport.convertToViewportPoint(a.rect[2], a.rect[3]),
                  ]);
                  return {
                    id: a.id,
                    url: a.url,
                    dest: a.dest,
                    style: {
                      left: rect[0],
                      top: rect[1],
                      width: rect[2] - rect[0],
                      height: rect[3] - rect[1],
                    },
                  };
                }),
            );
          page.cleanup();
        }
      })
      .catch((error) => {
        if (error.status === 401)
          window.dispatchEvent(new Event("session-expired"));
        if (active) setState("error");
      });
    return () => {
      active = false;
      render.cancel();
    };
  }, [pdf, number, width, zoom, thumbnail]);
  async function follow(dest) {
    const resolved =
      typeof dest === "string" ? await pdf.getDestination(dest) : dest;
    if (resolved)
      go(
        typeof resolved[0] === "number"
          ? resolved[0] + 1
          : (await pdf.getPageIndex(resolved[0])) + 1,
      );
  }
  return (
    <div
      className={`pdf-sheet ${thumbnail ? "pdf-mini" : ""}`}
      data-state={state}
      style={{ width: (width * zoom) / 100 }}
    >
      <div className="pdf-raster" ref={raster} />
      {!thumbnail && (
        <>
          {links.map((link) =>
            link.url && /^(https?:|mailto:)/i.test(link.url) ? (
              <a
                key={link.id}
                className="pdf-link"
                style={link.style}
                href={link.url}
                target="_blank"
                rel="noopener noreferrer"
                aria-label="Abrir link da publicação"
              />
            ) : link.dest ? (
              <button
                key={link.id}
                className="pdf-link"
                style={link.style}
                aria-label="Ir para página vinculada"
                onClick={() => follow(link.dest).catch(() => {})}
              />
            ) : null,
          )}
        </>
      )}
      {state === "loading" && (
        <span className="pdf-state" role="status">
          Carregando página {number}…
        </span>
      )}
      {state === "error" && (
        <span className="pdf-state" role="alert">
          {thumbnail ? (
            "Miniatura indisponível."
          ) : (
            <>
              Não foi possível exibir a página {number}.{" "}
              <button type="button" onClick={retry}>
                Tentar carregar novamente
              </button>
            </>
          )}
        </span>
      )}
    </div>
  );
}
function Thumbnails({ pdf, page, total, go, edition }) {
  const [top, setTop] = useState(0);
  const ref = useRef(null);
  useEffect(() => {
    if (ref.current)
      ref.current.scrollTop = Math.max(
        0,
        Math.floor((page - 1) / 2) * 112 - 112,
      );
  }, [page]);
  return (
    <div
      ref={ref}
      className="virtual-thumbnails"
      aria-label="Miniaturas das páginas"
      onScroll={(e) => setTop(e.currentTarget.scrollTop)}
    >
      <div style={{ height: Math.ceil(total / 2) * 112, position: "relative" }}>
        {thumbnailWindow(top, total).map((n) => (
          <button
            key={n}
            aria-label={`Abrir página ${n}`}
            aria-current={n === page ? "page" : undefined}
            onClick={() => go(n)}
            className={n === page ? "active" : ""}
            style={{
              position: "absolute",
              top: Math.floor((n - 1) / 2) * 112,
              left: (n - 1) % 2 ? "50%" : 0,
            }}
          >
            {n === 1 ? (
              <img src={edition.cover} alt="Capa" />
            ) : (
              <PdfPage pdf={pdf} number={n} width={60} thumbnail />
            )}
            <span>{n}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
function normalize(text) {
  return text
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase();
}
function PdfSearch({ pdf, go }) {
  const [query, setQuery] = useState(""),
    [state, setState] = useState({ busy: false, results: [], message: "" });
  const job = useRef(0);
  useEffect(
    () => () => {
      job.current++;
    },
    [pdf],
  );
  async function search(event) {
    event.preventDefault();
    const token = ++job.current;
    if (!query.trim()) {
      setState({ busy: false, results: [], message: "" });
      return;
    }
    setState({ busy: true, results: [], message: "Pesquisando…" });
    const results = [];
    const term = normalize(query.trim());
    try {
      for (let n = 1; n <= pdf.numPages; n++) {
        if (token !== job.current) return;
        const page = await pdf.getPage(n),
          content = await page.getTextContent();
        const text = content.items.map((item) => item.str || "").join(" ");
        page.cleanup();
        if (normalize(text).includes(term)) results.push(n);
      }
      if (token === job.current)
        setState({
          busy: false,
          results,
          message: results.length
            ? `${results.length} páginas encontradas.`
            : "Texto não encontrado. PDFs digitalizados podem não conter texto pesquisável.",
        });
    } catch {
      if (token === job.current)
        setState({
          busy: false,
          results: [],
          message: "Não foi possível concluir a busca.",
        });
    }
  }
  return (
    <div className="pdf-search">
      <form onSubmit={search}>
        <label htmlFor="pdf-search">Buscar no PDF</label>
        <div>
          <input
            id="pdf-search"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Palavra ou expressão"
          />
          <button disabled={state.busy} aria-label="Pesquisar texto">
            <Icon name="search" size={16} />
          </button>
        </div>
      </form>
      {state.busy && (
        <button
          type="button"
          onClick={() => {
            job.current++;
            setState({ busy: false, results: [], message: "Busca cancelada." });
          }}
        >
          Cancelar busca
        </button>
      )}
      <small role="status">{state.message}</small>
      <div className="pdf-search-results">
        {state.results.map((n) => (
          <button key={n} onClick={() => go(n)}>
            Página {n}
          </button>
        ))}
      </div>
    </div>
  );
}
export default function Reader() {
  const { slug } = useParams(),
    [params] = useSearchParams(),
    preview = params.get("preview"),
    version = params.get("version");
  const [source, setSource] = useState({ loading: true }),
    [attempt, setAttempt] = useState(0);
  const [animation, setAnimation] = useState(true);
  const [pageMode, setPageMode] = useState(null),
    [isMobile, setIsMobile] = useState(() =>
      window.matchMedia("(max-width: 800px)").matches,
    );
  const [page, setPage] = useState(1),
    [draft, setDraft] = useState("1"),
    [zoom, setZoom] = useState(100),
    [direction, setDirection] = useState(1);
  const [size, setSize] = useState(800),
    [height, setHeight] = useState(700),
    [fullscreen, setFullscreen] = useState(false),
    [notice, setNotice] = useState("");
  const root = useRef(null),
    canvasArea = useRef(null),
    touch = useRef(null),
    currentPage = useRef(1),
    turnId = useRef(0),
    recovery = useRef(null);
  const retry = useCallback(() => {
    const key = `${slug}:${preview}:${version}`;
    const previous = recovery.current?.key === key ? recovery.current : null;
    recovery.current = {
      key,
      page: source.edition
        ? currentPage.current
        : previous?.page || currentPage.current,
      document: source.edition?.document_version || previous?.document,
    };
    setAttempt((n) => n + 1);
  }, [slug, preview, version, source.edition]);
  const reducedMotion = useReducedMotion();
  useEffect(() => {
    const media = window.matchMedia("(max-width: 800px)");
    const update = () => setIsMobile(media.matches);
    media.addEventListener("change", update);
    return () => media.removeEventListener("change", update);
  }, []);
  useEffect(() => {
    const controller = new AbortController();
    let task;
    const started = window.performance.now();
    const bookmark =
      recovery.current?.key === `${slug}:${preview}:${version}`
        ? recovery.current
        : null;
    const documentVersion = version || bookmark?.document;
    const query = documentVersion
      ? `?document=${encodeURIComponent(documentVersion)}`
      : "";
    setSource({ loading: true });
    setPage(1);
    currentPage.current = 1;
    setDraft("1");
    setZoom(100);
    request(
      preview
        ? `/admin/publications/${preview}${query}`
        : `/public/publications/${slug}${query}`,
      { signal: controller.signal },
    )
      .then(async (row) => {
        if (controller.signal.aborted) return;
        if (row.processing_state !== "ready" || !row.file_url)
          throw { userMessage: "O PDF ainda não está pronto para leitura." };
        task = getDocument({
          url: row.file_url,
          withCredentials: true,
          rangeChunkSize: 65536,
          disableAutoFetch: true,
          disableStream: true,
          isEvalSupported: false,
          enableXfa: false,
          cMapUrl: "/pdfjs/cmaps/",
          cMapPacked: true,
          standardFontDataUrl: "/pdfjs/standard_fonts/",
          wasmUrl: "/pdfjs/wasm/",
        });
        const pdf = await task.promise;
        if (controller.signal.aborted) return;
        if (pdf.numPages > 300)
          throw { userMessage: "O limite de leitura é de 300 páginas." };
        const firstPage = await pdf.getPage(1);
        const viewport = firstPage.getViewport({ scale: 1 });
        if (!controller.signal.aborted) {
          const restored = clampPage(bookmark?.page || 1, pdf.numPages);
          setPage(restored);
          currentPage.current = restored;
          setDraft(String(restored));
          setSource({
            loading: false,
            readyMs: Math.round(window.performance.now() - started),
            pdf,
            ratio: viewport.width / viewport.height,
            edition: editionFromApi(row),
          });
        }
      })
      .catch((error) => {
        if (error.status === 401 && preview)
          window.dispatchEvent(new Event("session-expired"));
        if (!controller.signal.aborted)
          setSource({ loading: false, error: readerError(error) });
      });
    return () => {
      controller.abort();
      void task?.destroy();
    };
  }, [slug, preview, version, attempt]);
  useEffect(() => {
    if (!canvasArea.current) return;
    const observer = new ResizeObserver((entries) => {
      setSize(entries[0].contentRect.width);
      setHeight(entries[0].contentRect.height);
    });
    observer.observe(canvasArea.current);
    return () => observer.disconnect();
  }, [source.loading]);
  const total = source.pdf?.numPages || 1,
    double = pageMode ? pageMode === "double" : defaultDoublePage(isMobile),
    visible = visiblePages(page, total, double);
  const go = useCallback(
    (value, flip = false) => {
      const n = clampPage(value, total);
      if (n === currentPage.current) {
        setDraft(String(n));
        return;
      }
      setDirection(n >= currentPage.current ? 1 : -1);
      if (flip && animation && !reducedMotion) {
        setTurn({
          id: ++turnId.current,
          from: visiblePages(currentPage.current, total, double),
          to: visiblePages(n, total, double),
        });
      } else {
        setTurn(null);
      }
      currentPage.current = n;
      setPage(n);
      setDraft(String(n));
    },
    [animation, double, reducedMotion, total],
  );
  const step = useCallback(
    (direction) =>
      go(stepPage(currentPage.current, total, double, direction), true),
    [go, total, double],
  );
  const [turn, setTurn] = useState(null);
  useEffect(() => {
    const key = (event) => {
      if (
        event.ctrlKey ||
        event.metaKey ||
        event.altKey ||
        event.target.closest("input,textarea,select,[contenteditable]")
      )
        return;
      if (
        [
          "ArrowRight",
          "PageDown",
          "ArrowLeft",
          "PageUp",
          "Home",
          "End",
        ].includes(event.key)
      ) {
        event.preventDefault();
        if (event.key === "Home") go(1);
        else if (event.key === "End") go(total);
        else step(["ArrowRight", "PageDown"].includes(event.key) ? 1 : -1);
      }
    };
    window.addEventListener("keydown", key);
    return () => window.removeEventListener("keydown", key);
  }, [go, step, total]);
  useEffect(() => {
    const change = () =>
      setFullscreen(document.fullscreenElement === root.current);
    document.addEventListener("fullscreenchange", change);
    return () => document.removeEventListener("fullscreenchange", change);
  }, []);
  async function toggleFullscreen() {
    try {
      if (document.fullscreenElement) await document.exitFullscreen();
      else await root.current.requestFullscreen();
    } catch {
      setNotice(
        "Seu navegador não permitiu tela cheia. Você pode continuar a leitura nesta janela.",
      );
    }
  }
  if (source.loading)
    return (
      <div className="access-message" role="status">
        Carregando revista…
      </div>
    );
  if (source.error)
    return (
      <div className="access-message" role="alert">
        <p>{source.error}</p>
        <button className="button primary" onClick={retry}>
          Tentar novamente
        </button>
        <Link className="button secondary" to="/edicoes">
          Voltar às edições
        </Link>
      </div>
    );
  const { pdf, edition: e } = source;
  const width = fittedPageWidth(
    size,
    height,
    visible.length,
    source.ratio || 0.707,
  );
  const pageHeight = width / (source.ratio || 0.707);
  const spreadWidth =
    visible.length * width + (visible.length > 1 ? 2 : 0) + 32;
  const back = preview ? `/admin/publicacoes/${preview}` : `/edicoes/${e.slug}`;
  return (
    <div
      ref={root}
      className="reader-app real-reader"
      data-document-ready-ms={source.readyMs}
    >
      <header className="reader-header">
        <Brand compact />
        <nav>
          <Link to="/">Início</Link>
          <Link to="/edicoes">Edições</Link>
          <Link to="/temas">Temas</Link>
          <Link to="/acervo">Acervo</Link>
        </nav>
      </header>
      <main className="reader-layout">
        <aside className="reader-sidebar">
          <Link to={back} className="reader-back">
            <Icon name="back" size={17} />
            Voltar para a edição
          </Link>
          <div className="reader-edition">
            <Cover edition={e} />
            <strong>{e.issue}</strong>
            <span>
              {e.month} de {e.year}
            </span>
            <h3>{e.title}</h3>
          </div>
          <PdfSearch pdf={pdf} go={go} />
          {size >= 580 && (
            <Thumbnails
              pdf={pdf}
              page={page}
              total={total}
              go={go}
              edition={e}
            />
          )}
        </aside>
        <section className="reader-workspace">
          <div className="reader-toolbar">
            <button
              aria-label="Página anterior"
              disabled={visible[0] === 1}
              onClick={() => step(-1)}
            >
              ‹
            </button>
            <button
              aria-label="Próxima página"
              disabled={visible.at(-1) === total}
              onClick={() => step(1)}
            >
              ›
            </button>
            <form
              className="page-counter"
              onSubmit={(event) => {
                event.preventDefault();
                go(Number(draft));
              }}
            >
              <input
                aria-label="Número da página"
                type="number"
                min="1"
                max={total}
                value={draft}
                onChange={(e) => setDraft(e.target.value)}
                onBlur={() => go(Number(draft))}
              />
              <span>/ {total}</span>
            </form>
            <i />
            <button
              aria-label="Diminuir zoom"
              disabled={zoom <= 60}
              onClick={() => setZoom((z) => Math.max(60, z - 10))}
            >
              −
            </button>
            <strong>{zoom}%</strong>
            <button
              aria-label="Aumentar zoom"
              disabled={zoom >= 200}
              onClick={() => setZoom((z) => Math.min(200, z + 10))}
            >
              +
            </button>
            <button className="fit-button" onClick={() => setZoom(100)}>
              Ajustar
            </button>
            <div className="page-mode" role="group" aria-label="Páginas por tela">
              <button
                className="fit-button page-mode-option"
                aria-pressed={!double}
                onClick={() => setPageMode("single")}
              >
                1 página
              </button>
              <button
                className="fit-button page-mode-option"
                aria-pressed={double}
                onClick={() => setPageMode("double")}
              >
                2 páginas
              </button>
            </div>
            <button
              className="fit-button motion-toggle"
              aria-label="Animação de páginas"
              aria-pressed={animation && !reducedMotion}
              onClick={() => setAnimation((v) => !v)}
            >
              {animation && !reducedMotion ? "Animação" : "Sem animação"}
            </button>
            <i />
            <button
              aria-label={fullscreen ? "Sair da tela cheia" : "Tela cheia"}
              onClick={toggleFullscreen}
            >
              <Icon name="fullscreen" size={19} />
            </button>
          </div>
          <p className="reader-announcement" aria-live="polite">
            {visible.length > 1
              ? `Páginas ${visible.join(" e ")}`
              : `Página ${page}`}{" "}
            de {total}
          </p>
          {notice && <p role="status">{notice}</p>}
          <div
            ref={canvasArea}
            className="reader-canvas"
            style={{
              touchAction:
                zoom > 100 ? "pan-x pan-y pinch-zoom" : "pan-y pinch-zoom",
            }}
            onPointerDown={(event) => {
              if (event.pointerType === "touch")
                touch.current = { x: event.clientX, y: event.clientY };
            }}
            onPointerUp={(event) => {
              const start = touch.current;
              touch.current = null;
              if (start && zoom <= 100 && !window.getSelection()?.toString()) {
                const dx = event.clientX - start.x,
                  dy = event.clientY - start.y;
                if (Math.abs(dx) > 60 && Math.abs(dx) > Math.abs(dy) * 1.5)
                  step(dx < 0 ? 1 : -1);
              }
            }}
            onPointerCancel={() => {
              touch.current = null;
            }}
          >
            <div
              className="reader-stage"
              style={{ minWidth: (spreadWidth * zoom) / 100 }}
            >
              <PageTurn
                direction={direction}
                double={double}
                turn={turn}
                pageWidth={(width * zoom) / 100}
                pageHeight={(pageHeight * zoom) / 100}
                spreadWidth={spreadWidth * (zoom / 100)}
                renderPage={(n) => (
                  <PdfPage
                    key={`turn-${turn?.id}-${n}:${width}:${zoom}`}
                    pdf={pdf}
                    number={n}
                    width={width}
                    zoom={zoom}
                    go={go}
                    retry={retry}
                  />
                )}
                onTurnComplete={(id) =>
                  setTurn((current) => (current?.id === id ? null : current))
                }
              >
                <div
                  className={`pdf-open-pages ${visible.length === 1 ? "single-page" : ""}`}
                >
                  {visible.map((n) => (
                    <PdfPage
                      key={`${n}:${width}:${zoom}`}
                      pdf={pdf}
                      number={n}
                      width={width}
                      zoom={zoom}
                      go={go}
                      retry={retry}
                    />
                  ))}
                </div>
              </PageTurn>
            </div>
          </div>
          <div className="reader-bottom">
            <Link className="button secondary" to={back}>
              <Icon name="back" />
              Voltar para a edição
            </Link>
            <div />
            {e.download_url && (
              <a className="button secondary" href={e.download_url}>
                <Icon name="download" />
                Baixar PDF
              </a>
            )}
            <button className="button secondary" onClick={retry}>
              Recarregar PDF
            </button>
            <button className="button secondary" onClick={toggleFullscreen}>
              <Icon name="fullscreen" />
              Tela cheia
            </button>
          </div>
        </section>
      </main>
    </div>
  );
}
