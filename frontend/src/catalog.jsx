import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react";
import { request } from "./api";
import { useAuth } from "./auth";
const Context = createContext(null);
export function editionFromApi(row) {
  const date = new Date(row.publication_date + "T12:00:00");
  return {
    ...row,
    month: date.toLocaleString("pt-BR", { month: "long" }),
    year: date.getFullYear(),
    subtitle: row.description,
    pages: row.page_count,
    cover: row.cover_url,
    categories: row.categories.map((c) => c.name),
    rating: Number(row.rating_average).toFixed(1),
    ratings: row.rating_count,
    status: {
      draft: "Rascunho",
      published: "Publicado",
      archived: "Arquivado",
    }[row.status],
    raw: row,
  };
}
export async function all(path, signal) {
  const rows = [];
  let page = 1;
  while (true) {
    const data = await request(
      `${path}${path.includes("?") ? "&" : "?"}page_size=100&page=${page}`,
      {
        signal,
      },
    );
    rows.push(...data.results);
    if (!data.next) return rows;
    page++;
  }
}
export function CatalogProvider({ children }) {
  const { user } = useAuth();
  const [version, setVersion] = useState(0);
  const [state, setState] = useState({
    editions: [],
    categories: [],
    ready: false,
    error: "",
  });
  const [admin, setAdmin] = useState({ rows: [], ready: false, error: "" });
  const refresh = useCallback(() => setVersion((n) => n + 1), []);
  useEffect(() => {
    const controller = new AbortController();
    (async () => {
      const settings = await request("/public/settings", {
        signal: controller.signal,
      });
      const [rows, categories, metadata] = settings.public_archive_enabled
        ? await Promise.all([
            all("/public/publications", controller.signal),
            all("/public/categories", controller.signal),
            request("/public/catalog", { signal: controller.signal }),
          ])
        : [[], [], { years: [], total: 0, featured: null }];
      if (!controller.signal.aborted)
        setState({
          editions: rows.map(editionFromApi),
          categories,
          settings,
          metadata: {
            ...metadata,
            featured: metadata.featured
              ? editionFromApi(metadata.featured)
              : null,
          },
          ready: true,
          error: "",
        });
    })().catch((error) => {
      if (!controller.signal.aborted)
        setState((s) => ({ ...s, ready: true, error: error.message }));
    });
    return () => controller.abort();
  }, [version]);
  useEffect(() => {
    const controller = new AbortController();
    if (user) {
      setAdmin({ rows: [], categories: [], ready: false, error: "" });
      Promise.all([
        all("/admin/publications", controller.signal),
        all("/admin/categories", controller.signal),
      ])
        .then(([rows, categories]) => {
          if (controller.signal.aborted) return;
          setAdmin({
            rows: rows.map(editionFromApi),
            categories,
            ready: true,
            error: "",
          });
        })
        .catch((error) => {
          if (!controller.signal.aborted)
            setAdmin({ rows: [], ready: true, error: error.message });
        });
    } else setAdmin({ rows: [], ready: false, error: "" });
    return () => controller.abort();
  }, [user, version]);
  return (
    <Context.Provider
      value={{
        ...state,
        adminRows: admin.rows,
        adminCategories: admin.categories || [],
        adminReady: admin.ready,
        adminError: admin.error,
        refresh,
      }}
    >
      {children}
    </Context.Provider>
  );
}
export function useCatalog() {
  return useContext(Context);
}
