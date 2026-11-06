import { lazy, Suspense, useEffect, useMemo, useState } from "react";
import {
  Link,
  NavLink,
  Route,
  Routes,
  useLocation,
  useNavigate,
  useParams,
  useSearchParams,
} from "react-router-dom";
import { useCatalog } from "./catalog";
import { request } from "./api";
import { AdminLayout } from "./admin-layout";
import {
  PeopleAdmin,
  UsersAdmin,
  SettingsAdmin,
  AuditAdmin,
} from "./editorial-admin";
import { CategoriesAdmin } from "./categories-admin";
import { Icon, Brand, Cover } from "./ui";
import { NewPublication, EditPublication } from "./publications";
const Reader = lazy(() => import("./reader/Reader"));
import { RequireAuth, useAuth } from "./auth";
import "./styles.css";

const searchText = (text) =>
  text
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase();
function Header() {
  const navigate = useNavigate();
  const [q, setQ] = useState("");
  const submit = (e) => {
    e.preventDefault();
    navigate(
      q.trim() ? `/buscar?q=${encodeURIComponent(q.trim())}` : "/buscar",
    );
  };
  return (
    <header className="site-header">
      <div className="container header-grid">
        <Brand />
        <nav className="main-nav">
          <NavLink to="/">Início</NavLink>
          <NavLink to="/edicoes">Edições</NavLink>
          <NavLink to="/temas">Temas</NavLink>
          <NavLink to="/acervo">Acervo</NavLink>
          <NavLink to="/sobre">Sobre</NavLink>
        </nav>
        <div className="header-right">
          <small className="header-tagline">
            Sua escolha para um grande futuro.
          </small>
          <form className="header-search" onSubmit={submit}>
            <Icon name="search" size={17} />
            <input
              aria-label="Buscar na revista"
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="Buscar na revista..."
            />
          </form>
        </div>
      </div>
    </header>
  );
}
function Footer() {
  return (
    <footer className="site-footer">
      <div className="container footer-grid">
        <Brand compact variant="footer" />
        <nav>
          <Link to="/sobre">Sobre a Revista</Link>
          <Link to="/sobre#normas">Normas para Autores</Link>
          <Link to="/sobre#politica">Política Editorial</Link>
          <Link to="/sobre#contato">Contato</Link>
        </nav>
        <div className="footer-tagline">Ciência. Pessoas. Possibilidades.</div>
      </div>
    </footer>
  );
}
function PublicLayout({ children }) {
  return (
    <>
      <Header />
      {children}
      <Footer />
    </>
  );
}
function ArrowLink({ to, children }) {
  return (
    <Link to={to} className="arrow-link">
      <span>{children}</span>
      <Icon name="arrow" size={17} />
    </Link>
  );
}
function SectionHeading({ children, action }) {
  return (
    <div className="section-heading">
      <h2>{children}</h2>
      {action}
    </div>
  );
}

function Home() {
  const { editions, categories, settings, metadata } = useCatalog();
  const featured = metadata?.featured || editions[0];
  if (!featured)
    return (
      <PublicLayout>
        <main className="empty-catalog">
          <h1>{settings?.name || "Revista Científica de Psicologia"}</h1>
          <p>As edições publicadas aparecerão aqui.</p>
          <Link className="button secondary" to="/admin">
            Área editorial
          </Link>
        </main>
      </PublicLayout>
    );
  return (
    <PublicLayout>
      <main>
        <section className="hero">
          <div className="container hero-grid">
            <Cover edition={featured} className="hero-cover" />
            <div className="hero-copy">
              <div className="section-kicker">EDIÇÃO EM DESTAQUE</div>
              <h1>{settings?.name || "Revista Científica de Psicologia"}</h1>
              <div className="hero-meta">
                {featured.issue}
                <span>•</span>
                {featured.month} de {featured.year}
              </div>
              <h3>{featured.title}</h3>
              <p>{featured.subtitle}</p>
              <div className="publication-meta">
                {featured.pages} páginas{" "}
                {settings?.issn && (
                  <>
                    <span />
                    ISSN {settings.issn}
                  </>
                )}
              </div>
              <div className="actions">
                <Link to={`/ler/${featured.slug}`} className="button primary">
                  <Icon name="book" />
                  Ler edição
                </Link>
                {featured.download_url && (
                  <a className="button secondary" href={featured.download_url}>
                    <Icon name="download" />
                    Baixar PDF
                  </a>
                )}
              </div>
            </div>
            <aside className="hero-statement">
              <i />
              <h2>
                Conhecimento
                <br />
                para uma sociedade
                <br />
                mais humana.
              </h2>
              <p>
                A Revista Científica de Psicologia da UNIEURO publica pesquisas,
                reflexões e práticas que contribuem para o desenvolvimento
                humano e uma sociedade mais justa.
              </p>
            </aside>
          </div>
        </section>
        <section className="container home-section">
          <SectionHeading
            action={<ArrowLink to="/edicoes">Ver todas as edições</ArrowLink>}
          >
            Edições recentes
          </SectionHeading>
          <div className="recent-editions">
            {editions.slice(1, 5).map((e) => (
              <article className="recent-edition" key={e.id}>
                <Cover edition={e} />
                <div className="recent-info">
                  <strong>{e.issue}</strong>
                  <span>
                    {e.month.slice(0, 3).toUpperCase()} {e.year}
                  </span>
                  <h3>{e.title}</h3>
                  <small>{e.pages} páginas</small>
                  <ArrowLink to={`/edicoes/${e.slug}`}>Ver edição</ArrowLink>
                </div>
              </article>
            ))}
          </div>
        </section>
        <section className="container home-section topics-section">
          <SectionHeading>Explore por tema</SectionHeading>
          <div className="topics-row">
            {categories.slice(0, 5).map((c) => (
              <Link className="topic-card" key={c.slug} to={`/temas/${c.slug}`}>
                <Icon name={c.icon} size={28} />
                <span>{c.name}</span>
                <Icon name="arrow" size={16} />
              </Link>
            ))}
          </div>
        </section>
        <section className="container archive-bar">
          <h2>Acervo</h2>
          <Link className="year-active" to="/acervo">
            Todos
          </Link>
          {(metadata?.years || [...new Set(editions.map((e) => e.year))]).map(
            (y) => (
              <Link key={y} to={`/acervo?ano=${y}`}>
                {y}
              </Link>
            ),
          )}
          <ArrowLink to="/acervo">Ver acervo completo</ArrowLink>
        </section>
      </main>
    </PublicLayout>
  );
}

function PageNav({ page, total, size = 12, onChange }) {
  const pages = Math.max(1, Math.ceil(total / size)),
    current = Math.min(page, pages);
  return (
    pages > 1 && (
      <nav className="admin-pagination" aria-label="Paginação de edições">
        <button
          className="button secondary"
          disabled={current === 1}
          onClick={() => onChange(current - 1)}
        >
          Anterior
        </button>
        <span>
          Página {current} de {pages}
        </span>
        <button
          className="button secondary"
          disabled={current === pages}
          onClick={() => onChange(current + 1)}
        >
          Próxima
        </button>
      </nav>
    )
  );
}
function slicePage(rows, page, size = 12) {
  const current = Math.min(page, Math.max(1, Math.ceil(rows.length / size)));
  return rows.slice((current - 1) * size, current * size);
}

function Editions() {
  const [page, setPage] = useState(1);
  const { editions, categories } = useCatalog();
  const [sort, setSort] = useState("recent");
  const [year, setYear] = useState("Todos");
  const [topic, setTopic] = useState("Todos");
  const [q, setQ] = useState("");
  const years = [...new Set(editions.map((e) => e.year))];
  const filtered = useMemo(
    () =>
      editions.filter(
        (e) =>
          (year === "Todos" || e.year === Number(year)) &&
          (topic === "Todos" || e.categories.includes(topic)) &&
          (!q.trim() ||
            searchText(
              `${e.title} ${e.subtitle} ${e.categories.join(" ")}`,
            ).includes(searchText(q))),
      ),
    [year, topic, q, editions],
  );
  return (
    <PublicLayout>
      <main className="container page catalog-page">
        <header className="page-title">
          <h1>Edições da Revista Científica de Psicologia</h1>
          <p>
            Explore todas as edições, filtre por ano ou tema e encontre os
            conteúdos que mais lhe interessam.
          </p>
        </header>
        <div className="filter-panel">
          <label>
            <span>Filtrar por ano</span>
            <select value={year} onChange={(e) => setYear(e.target.value)}>
              <option>Todos</option>
              {years.map((y) => (
                <option key={y}>{y}</option>
              ))}
            </select>
          </label>
          <label>
            <span>Filtrar por tema</span>
            <select value={topic} onChange={(e) => setTopic(e.target.value)}>
              <option>Todos</option>
              {categories.map((c) => (
                <option key={c.slug}>{c.name}</option>
              ))}
            </select>
          </label>
          <label className="filter-search">
            <span>Buscar por palavra-chave</span>
            <div>
              <Icon name="search" size={17} />
              <input
                value={q}
                onChange={(e) => setQ(e.target.value)}
                placeholder="Ex.: saúde mental, educação..."
              />
            </div>
          </label>
        </div>
        <div className="catalog-summary">
          <h2>{filtered.length} edições encontradas</h2>
          <select
            aria-label="Ordenar"
            value={sort}
            onChange={(e) => setSort(e.target.value)}
          >
            <option value="recent">Mais recentes</option>
            <option value="old">Mais antigas</option>
          </select>
        </div>
        <div className="catalog-grid">
          {slicePage(
            sort === "old" ? [...filtered].reverse() : filtered,
            page,
          ).map((e) => (
            <article className="catalog-card" key={e.id}>
              <Link to={`/edicoes/${e.slug}`}>
                <Cover edition={e} />
              </Link>
              <div>
                <strong>{e.issue}</strong>
                <span>
                  {e.month} de {e.year}
                </span>
                <h3>{e.title}</h3>
                <small>{e.pages} páginas</small>
                <ArrowLink to={`/edicoes/${e.slug}`}>Ver edição</ArrowLink>
              </div>
            </article>
          ))}
        </div>
        <PageNav page={page} total={filtered.length} onChange={setPage} />
        <div className="catalog-topics">
          <SectionHeading>Explore por tema</SectionHeading>
          <div className="topics-row">
            {categories.slice(0, 5).map((c) => (
              <Link className="topic-card" key={c.slug} to={`/temas/${c.slug}`}>
                <Icon name={c.icon} size={27} />
                <span>{c.name}</span>
                <Icon name="arrow" size={16} />
              </Link>
            ))}
          </div>
        </div>
      </main>
    </PublicLayout>
  );
}

function EditionDetail() {
  const { editions, refresh, settings } = useCatalog();
  const { slug } = useParams();
  const e = editions.find((x) => x.slug === slug);
  const [rating, setRating] = useState(0);
  const [ratingError, setRatingError] = useState("");
  useEffect(() => {
    const controller = new AbortController();
    if (!settings?.ratings_enabled) return;
    request(`/public/publications/${slug}/rating`, {
      signal: controller.signal,
    })
      .then((data) => setRating(data.score || 0))
      .catch((error) => {
        if (!controller.signal.aborted) setRatingError(error.message);
      });
    return () => controller.abort();
  }, [slug, settings?.ratings_enabled]);
  async function rate(score) {
    try {
      await request(`/public/publications/${slug}/rating`, {
        method: "POST",
        body: JSON.stringify({ score }),
      });
      setRating(score);
      setRatingError("");
      refresh();
    } catch (error) {
      setRatingError(error.message);
    }
  }
  if (!e)
    return (
      <PublicLayout>
        <main className="empty-catalog">
          <h1>Edição não encontrada</h1>
          <Link to="/edicoes">Voltar às edições</Link>
        </main>
      </PublicLayout>
    );
  return (
    <PublicLayout>
      <main className="container page">
        <Link className="back-link" to="/edicoes">
          <Icon name="back" size={17} />
          Todas as edições
        </Link>
        <section className="edition-detail">
          <Cover edition={e} className="detail-cover" />
          <div>
            <div className="section-kicker">
              {e.issue} · {e.month.toUpperCase()} {e.year}
            </div>
            <h1>{e.title}</h1>
            <p className="detail-lead">{e.subtitle}</p>
            <div className="category-chips">
              {e.categories.map((c) => (
                <span key={c}>{c}</span>
              ))}
            </div>
            <div className="detail-facts">
              <div>
                <span>Páginas</span>
                <strong>{e.pages}</strong>
              </div>
              {settings?.ratings_enabled && (
                <div>
                  <span>Avaliação</span>
                  <strong>★ {e.rating}</strong>
                </div>
              )}
              <div>
                <span>Formato</span>
                <strong>PDF</strong>
              </div>
            </div>
            <div className="actions">
              <Link className="button primary" to={`/ler/${e.slug}`}>
                <Icon name="book" />
                Ler revista
              </Link>
              {e.download_url && (
                <a className="button secondary" href={e.download_url}>
                  <Icon name="download" />
                  Baixar PDF
                </a>
              )}
            </div>
          </div>
        </section>
        <section className="edition-about">
          <article>
            <h2>Sobre esta edição</h2>
            <p>
              {e.subtitle} A publicação reúne pesquisas, ensaios e reflexões
              desenvolvidos no contexto acadêmico do curso de Psicologia do
              Centro Universitário UNIEURO.
            </p>
            {e.authors?.length > 0 && (
              <>
                <h2>Autores</h2>
                <p>
                  {e.authors
                    .map(
                      (p) =>
                        p.name + (p.institution ? ` (${p.institution})` : ""),
                    )
                    .join("; ")}
                </p>
              </>
            )}
            {e.reviewers?.length > 0 && (
              <>
                <h2>Pareceristas</h2>
                <p>{e.reviewers.map((p) => p.name).join("; ")}</p>
              </>
            )}
            <h2>Informações da publicação</h2>
            <p>
              Centro Universitário UNIEURO · Curso de Psicologia · Revista
              científica digital.
            </p>
          </article>
          {settings?.ratings_enabled && (
            <aside>
              <h3>Avalie esta edição</h3>
              <p>Como foi sua experiência de leitura?</p>
              <div className="rating-stars">
                {[1, 2, 3, 4, 5].map((n) => (
                  <button
                    key={n}
                    className={n <= rating ? "active" : ""}
                    aria-label={`Avaliar com ${n} estrelas`}
                    onClick={() => rate(n)}
                  >
                    ★
                  </button>
                ))}
              </div>
              {ratingError && <small role="alert">{ratingError}</small>}
              {rating > 0 && <small>Avaliação registrada: {rating}/5</small>}
            </aside>
          )}
        </section>
      </main>
    </PublicLayout>
  );
}

function SearchPage() {
  const { editions } = useCatalog();
  const [params, setParams] = useSearchParams();
  const q = params.get("q") || "";
  const setQ = (q) => setParams(q ? { q } : {}, { replace: true });
  const results = editions.filter(
    (e) =>
      !q.trim() ||
      searchText(`${e.title} ${e.subtitle} ${e.categories.join(" ")}`).includes(
        searchText(q),
      ),
  );
  return (
    <PublicLayout>
      <main className="container page">
        <header className="page-title">
          <h1>Buscar publicações</h1>
          <p>
            Pesquise por título, tema ou informações cadastradas na revista.
          </p>
        </header>
        <div className="large-search">
          <Icon name="search" />
          <input
            autoFocus
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Digite sua busca..."
          />
        </div>
        <div className="search-results">
          {!results.length && <p>Nenhuma publicação encontrada.</p>}
          {results.map((e) => (
            <Link
              to={`/edicoes/${e.slug}`}
              key={e.id}
              className="search-result"
            >
              <Cover edition={e} />
              <div>
                <strong>
                  {e.issue} · {e.year}
                </strong>
                <h2>{e.title}</h2>
                <p>{e.subtitle}</p>
              </div>
              <Icon name="arrow" />
            </Link>
          ))}
        </div>
      </main>
    </PublicLayout>
  );
}
function Topics() {
  const { categories } = useCatalog();
  return (
    <PublicLayout>
      <main className="container page narrow">
        <header className="page-title">
          <h1>Temas</h1>
          <p>Explore as principais áreas da Psicologia presentes no acervo.</p>
        </header>
        <div className="topic-list">
          {categories.map((c) => (
            <Link to={`/temas/${c.slug}`} key={c.slug}>
              <Icon name={c.icon} size={30} />
              <div>
                <h2>{c.name}</h2>
                <p>{c.count} publicações no acervo</p>
              </div>
              <Icon name="arrow" />
            </Link>
          ))}
        </div>
      </main>
    </PublicLayout>
  );
}
function TopicPage() {
  const { categories, editions } = useCatalog();
  const { slug } = useParams();
  const c = categories.find((x) => x.slug === slug);
  if (!c)
    return (
      <PublicLayout>
        <main className="empty-catalog">Tema não encontrado.</main>
      </PublicLayout>
    );
  const list = editions.filter((e) => e.categories.includes(c.name));
  return (
    <PublicLayout>
      <main className="container page">
        <header className="page-title">
          <h1>{c.name}</h1>
          <p>{list.length} publicações encontradas.</p>
        </header>
        <div className="catalog-grid">
          {list.map((e) => (
            <article className="catalog-card" key={e.id}>
              <Cover edition={e} />
              <div>
                <strong>{e.issue}</strong>
                <span>
                  {e.month} de {e.year}
                </span>
                <h3>{e.title}</h3>
                <ArrowLink to={`/edicoes/${e.slug}`}>Ver edição</ArrowLink>
              </div>
            </article>
          ))}
        </div>
      </main>
    </PublicLayout>
  );
}
function Archive() {
  const { editions, metadata } = useCatalog();
  const [page, setPage] = useState(1);
  const [params, setParams] = useSearchParams();
  const years = metadata?.years || [...new Set(editions.map((e) => e.year))];
  const year = Number(params.get("ano")) || null;
  const setYear = (ano) => setParams(ano ? { ano } : {});
  const list = year ? editions.filter((e) => e.year === year) : editions;
  return (
    <PublicLayout>
      <main className="container page">
        <header className="page-title">
          <h1>Acervo</h1>
          <p>
            Todas as edições publicadas permanecem disponíveis para consulta.
          </p>
        </header>
        <div className="year-tabs">
          <button
            className={!year ? "active" : ""}
            onClick={() => setYear(null)}
          >
            Todos
          </button>
          {years.map((y) => (
            <button
              className={year === y ? "active" : ""}
              onClick={() => setYear(y)}
              key={y}
            >
              {y}
            </button>
          ))}
        </div>
        <div className="archive-list">
          {!list.length && <p>Nenhuma edição publicada neste período.</p>}
          {slicePage(list, page).map((e) => (
            <Link to={`/edicoes/${e.slug}`} key={e.id}>
              <div>
                {e.month.slice(0, 3).toUpperCase()}
                <small>{e.year}</small>
              </div>
              <Cover edition={e} />
              <div>
                <strong>{e.issue}</strong>
                <h2>{e.title}</h2>
                <p>{e.categories.join(" · ")}</p>
              </div>
              <Icon name="arrow" />
            </Link>
          ))}
        </div>
        <PageNav page={page} total={list.length} onChange={setPage} />
      </main>
    </PublicLayout>
  );
}
function About() {
  const { settings } = useCatalog();
  const location = useLocation();
  useEffect(() => {
    if (location.hash)
      document.getElementById(location.hash.slice(1))?.scrollIntoView();
  }, [location.hash]);
  return (
    <PublicLayout>
      <main className="container page prose">
        <h1>Sobre a revista</h1>
        <p>{settings?.description}</p>
        <h2>{settings?.name}</h2>
        {settings?.issn && <p>ISSN {settings.issn}</p>}
        <section id="normas">
          <h2>Normas para autores</h2>
          <p className="institutional-text">
            {settings?.author_guidelines ||
              "As normas serão publicadas pela equipe editorial."}
          </p>
        </section>
        <section id="politica">
          <h2>Política editorial</h2>
          <p className="institutional-text">
            {settings?.editorial_policy ||
              "A política editorial será publicada pela equipe responsável."}
          </p>
        </section>
        <section id="contato">
          <h2>Contato</h2>
          <p className="institutional-text">
            {settings?.contact_text || "Informações de contato em preparação."}
          </p>
          {settings?.contact_email && (
            <a href={`mailto:${settings.contact_email}`}>
              {settings.contact_email}
            </a>
          )}
        </section>
      </main>
    </PublicLayout>
  );
}

function AdminLogin() {
  const nav = useNavigate();
  const location = useLocation();
  const { signIn, user } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [saveCredentials, setSaveCredentials] = useState(false);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  async function submit(event) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      await signIn(email, password);
      nav(
        location.state?.from?.startsWith("/") &&
          !location.state.from.startsWith("//")
          ? location.state.from
          : "/admin",
        { replace: true },
      );
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }
  if (user)
    return (
      <div className="login-page">
        <div className="login-card">
          <p>Você já está conectado.</p>
          <Link className="button primary" to="/admin">
            Abrir painel
          </Link>
        </div>
      </div>
    );
  return (
    <div className="login-page">
      <div className="login-brand">
        <Brand />
      </div>
      <form
        className="login-card"
        autoComplete={saveCredentials ? "on" : "off"}
        onSubmit={submit}
      >
        <h1>Acesso administrativo</h1>
        <p>Revista Científica de Psicologia</p>
        <label>
          E-mail
          <input
            type="email"
            name="username"
            autoComplete={saveCredentials ? "username" : "off"}
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </label>
        <label>
          Senha
          <input
            type="password"
            name="password"
            autoComplete={saveCredentials ? "current-password" : "off"}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </label>
        <label className="login-remember">
          <input
            type="checkbox"
            checked={saveCredentials}
            onChange={(event) => setSaveCredentials(event.target.checked)}
          />
          <span>
            Salvar credenciais neste dispositivo
            <small>
              O gerenciador de senhas do navegador controla o armazenamento.
            </small>
          </span>
        </label>
        {error && <p role="alert">{error}</p>}
        <button className="button primary full" disabled={busy}>
          {busy ? "Entrando…" : "Entrar"}
        </button>
        <Link to="/">← Voltar ao site</Link>
      </form>
    </div>
  );
}
function Dashboard() {
  const { adminRows } = useCatalog();
  return (
    <AdminLayout
      title="Painel Administrativo"
      subtitle="Gerencie as edições, publicações e conteúdos da Revista Científica de Psicologia."
      action={
        <Link
          className="button primary admin-new-button"
          to="/admin/publicacoes/nova"
        >
          <Icon name="plus" />
          Nova publicação
        </Link>
      }
    >
      <div className="stats-grid">
        <Stat
          icon="file"
          label="Edições publicadas"
          value={adminRows.filter((e) => e.status === "Publicado").length}
          detail="Disponíveis no acervo"
        />
        <Stat
          icon="file"
          label="Rascunhos"
          value={adminRows.filter((e) => e.status === "Rascunho").length}
          detail="Em preparação"
        />
        <Stat
          icon="users"
          label="Arquivadas"
          value={adminRows.filter((e) => e.status === "Arquivado").length}
          detail="Fora do acervo público"
        />
        <Stat
          icon="eye"
          label="Total de páginas"
          value={adminRows.reduce((n, e) => n + e.pages, 0)}
          detail="PDFs processados"
        />
      </div>
      <PublicationTable rows={adminRows.slice(0, 5)} />
    </AdminLayout>
  );
}
function Stat({ icon, label, value, detail }) {
  return (
    <div className="stat-card">
      <div className="stat-icon">
        <Icon name={icon} />
      </div>
      <div className="stat-copy">
        <span>{label}</span>
        <strong>{value}</strong>
        <small>{detail}</small>
      </div>
    </div>
  );
}
function PublicationTable({ rows, showFilters = true }) {
  const [page, setPage] = useState(1);
  const { adminRows, categories, adminReady, adminError, refresh } =
    useCatalog();
  const [q, setQ] = useState(""),
    [year, setYear] = useState(""),
    [category, setCategory] = useState(""),
    [status, setStatus] = useState("");
  const data = rows || adminRows;
  const filtered = data.filter(
    (e) =>
      (!q || `${e.title} ${e.issue}`.toLowerCase().includes(q.toLowerCase())) &&
      (!year || e.year === Number(year)) &&
      (!category || e.categories.includes(category)) &&
      (!status || e.status === status),
  );
  return (
    <section className="admin-panel publications-panel">
      <div className="panel-heading">
        <h2>Edições da Revista</h2>
        <div className="panel-search">
          <Icon name="search" size={16} />
          <input
            aria-label="Buscar publicações"
            placeholder="Buscar por título ou edição..."
            value={q}
            onChange={(e) => setQ(e.target.value)}
          />
        </div>
      </div>
      {adminError && (
        <p role="alert">
          {adminError}
          <button onClick={refresh}>Tentar novamente</button>
        </p>
      )}
      {!adminReady && <p role="status">Carregando publicações…</p>}
      {showFilters && (
        <div className="table-filter-row">
          <span />
          <select
            aria-label="Ano"
            value={year}
            onChange={(e) => setYear(e.target.value)}
          >
            <option value="">Todos os anos</option>
            {[...new Set(data.map((e) => e.year))].map((y) => (
              <option key={y}>{y}</option>
            ))}
          </select>
          <select
            aria-label="Categoria"
            value={category}
            onChange={(e) => setCategory(e.target.value)}
          >
            <option value="">Todas as categorias</option>
            {categories.map((c) => (
              <option key={c.id}>{c.name}</option>
            ))}
          </select>
          <select
            aria-label="Status"
            value={status}
            onChange={(e) => setStatus(e.target.value)}
          >
            <option value="">Todos os status</option>
            {["Publicado", "Rascunho", "Arquivado"].map((s) => (
              <option key={s}>{s}</option>
            ))}
          </select>
        </div>
      )}
      <div className="table-scroll">
        <table>
          <thead>
            <tr>
              <th>Capa</th>
              <th>Título / Edição</th>
              <th>Categoria</th>
              <th>Ano</th>
              <th>Status</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            {slicePage(filtered, page, 10).map((e) => (
              <tr key={e.id}>
                <td>
                  <Cover edition={e} />
                </td>
                <td>
                  <b>{e.title}</b>
                  <small>
                    {e.issue} · {e.month} de {e.year}
                  </small>
                </td>
                <td>
                  <span className="category-pill">{e.categories[0]}</span>
                </td>
                <td>{e.year}</td>
                <td>
                  <span
                    className={`status-pill ${e.status === "Rascunho" ? "draft" : ""}`}
                  >
                    {e.status}
                  </span>
                </td>
                <td>
                  <div className="table-actions">
                    <Link
                      aria-label={`Visualizar ${e.title}`}
                      to={`/ler/${e.slug}?preview=${e.id}`}
                    >
                      <Icon name="eye" size={16} />
                    </Link>
                    <Link
                      aria-label={`Editar ${e.title}`}
                      to={`/admin/publicacoes/${e.id}`}
                    >
                      <Icon name="edit" size={16} />
                    </Link>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {adminReady && !filtered.length && (
          <p className="empty-catalog">Nenhuma publicação encontrada.</p>
        )}
      </div>
      <PageNav
        page={page}
        total={filtered.length}
        size={10}
        onChange={setPage}
      />
    </section>
  );
}
function Publications() {
  return (
    <AdminLayout
      title="Publicações"
      subtitle="Consulte, edite e organize todas as edições da revista."
      action={
        <Link className="button primary" to="/admin/publicacoes/nova">
          <Icon name="plus" />
          Nova publicação
        </Link>
      }
    >
      <PublicationTable />
    </AdminLayout>
  );
}
function RatingsAdmin() {
  const { editions } = useCatalog();
  return (
    <AdminLayout
      title="Avaliações"
      subtitle="Acompanhe a avaliação simples das edições."
    >
      <section className="admin-panel simple-admin-list">
        {editions.slice(0, 7).map((e) => (
          <div key={e.id}>
            <Cover edition={e} />
            <div>
              <strong>{e.title}</strong>
              <span>{e.ratings} avaliações</span>
            </div>
            <b>★ {e.rating}</b>
          </div>
        ))}
      </section>
    </AdminLayout>
  );
}
function CatalogGate({ children }) {
  const { ready, error, refresh, settings } = useCatalog();
  const location = useLocation();
  if (
    location.pathname.startsWith("/admin") ||
    location.pathname.startsWith("/ler/")
  )
    return children;
  if (!ready)
    return (
      <p className="access-message" role="status">
        Carregando acervo…
      </p>
    );
  if (error)
    return (
      <div className="access-message" role="alert">
        <p>{error}</p>
        <button className="button primary" onClick={refresh}>
          Tentar novamente
        </button>
      </div>
    );
  if (
    settings &&
    !settings.public_archive_enabled &&
    location.pathname !== "/sobre"
  )
    return (
      <PublicLayout>
        <main className="empty-catalog">
          <h1>Acervo temporariamente indisponível</h1>
          <p>O acesso público será reaberto pela equipe editorial.</p>
        </main>
      </PublicLayout>
    );
  return children;
}
function ReaderAccess() {
  const [params] = useSearchParams();
  return params.get("preview") ? (
    <RequireAuth>
      <Reader />
    </RequireAuth>
  ) : (
    <Reader />
  );
}
export default function App() {
  return (
    <Suspense
      fallback={
        <p className="access-message" role="status">
          Carregando leitor…
        </p>
      }
    >
      <CatalogGate>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/edicoes" element={<Editions />} />
          <Route path="/edicoes/:slug" element={<EditionDetail />} />
          <Route path="/ler/:slug" element={<ReaderAccess />} />
          <Route path="/buscar" element={<SearchPage />} />
          <Route path="/temas" element={<Topics />} />
          <Route path="/temas/:slug" element={<TopicPage />} />
          <Route path="/acervo" element={<Archive />} />
          <Route path="/sobre" element={<About />} />
          <Route path="/admin/login" element={<AdminLogin />} />
          <Route path="/admin" element={<Dashboard />} />
          <Route path="/admin/dashboard" element={<Dashboard />} />
          <Route path="/admin/publicacoes" element={<Publications />} />
          <Route path="/admin/publicacoes/nova" element={<NewPublication />} />
          <Route path="/admin/publicacoes/:id" element={<EditPublication />} />
          <Route path="/admin/categorias" element={<CategoriesAdmin />} />
          <Route path="/admin/avaliacoes" element={<RatingsAdmin />} />
          <Route
            path="/admin/autores"
            element={<PeopleAdmin key="author" kind="author" />}
          />
          <Route
            path="/admin/pareceristas"
            element={<PeopleAdmin key="reviewer" kind="reviewer" />}
          />
          <Route
            path="/admin/usuarios"
            element={
              <RequireAuth roles={["admin"]}>
                <UsersAdmin />
              </RequireAuth>
            }
          />
          <Route
            path="/admin/auditoria"
            element={
              <RequireAuth roles={["admin"]}>
                <AuditAdmin />
              </RequireAuth>
            }
          />
          <Route
            path="/admin/configuracoes"
            element={
              <RequireAuth roles={["admin"]}>
                <SettingsAdmin />
              </RequireAuth>
            }
          />
          <Route
            path="*"
            element={
              <PublicLayout>
                <main className="empty-catalog">
                  <h1>Página não encontrada</h1>
                  <Link to="/">Voltar ao início</Link>
                </main>
              </PublicLayout>
            }
          />
        </Routes>
      </CatalogGate>
    </Suspense>
  );
}
