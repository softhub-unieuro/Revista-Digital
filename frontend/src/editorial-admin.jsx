import { useCallback, useEffect, useState } from "react";
import { AdminLayout } from "./admin-layout";
import { request } from "./api";
import { useAuth } from "./auth";
import { useCatalog } from "./catalog";
import { Icon } from "./ui";

function useList(path) {
  const [page, setPage] = useState(1),
    [query, setQuery] = useState(""),
    [version, setVersion] = useState(0);
  const [state, setState] = useState({
    rows: [],
    count: 0,
    next: null,
    loading: true,
    error: "",
  });
  const refresh = useCallback(() => setVersion((n) => n + 1), []);
  useEffect(() => {
    const controller = new AbortController();
    setState((s) => ({ ...s, loading: true, error: "" }));
    request(
      `${path}${path.includes("?") ? "&" : "?"}page=${page}&q=${encodeURIComponent(query)}`,
      { signal: controller.signal },
    )
      .then((data) => {
        if (!controller.signal.aborted)
          setState({
            rows: data.results,
            count: data.count,
            next: data.next,
            loading: false,
            error: "",
          });
      })
      .catch((error) => {
        if (!controller.signal.aborted)
          setState((s) => ({ ...s, loading: false, error: error.message }));
      });
    return () => controller.abort();
  }, [path, page, query, version]);
  return {
    ...state,
    page,
    setPage,
    query,
    setQuery: (q) => {
      setPage(1);
      setQuery(q);
    },
    refresh,
  };
}
function ListControls({ list, placeholder = "Buscar pelo nome..." }) {
  return (
    <>
      <label className="admin-list-search">
        Buscar
        <input
          value={list.query}
          onChange={(e) => list.setQuery(e.target.value)}
          placeholder={placeholder}
        />
      </label>
      {list.loading && <p role="status">Carregando…</p>}
      {list.error && (
        <p role="alert">
          {list.error}
          <button className="text-button" onClick={list.refresh}>
            Tentar novamente
          </button>
        </p>
      )}
      {!list.loading && !list.rows.length && !list.error && (
        <p>Nenhum registro encontrado.</p>
      )}
    </>
  );
}
function Pages({ list }) {
  return (
    <nav className="admin-pagination" aria-label="Paginação">
      <button
        className="button secondary"
        disabled={list.page === 1 || list.loading}
        onClick={() => list.setPage((n) => n - 1)}
      >
        Anterior
      </button>
      <span>
        Página {list.page} · {list.count} registros
      </span>
      <button
        className="button secondary"
        disabled={!list.next || list.loading}
        onClick={() => list.setPage((n) => n + 1)}
      >
        Próxima
      </button>
    </nav>
  );
}

export function PeopleAdmin({ kind }) {
  const { user } = useAuth(),
    list = useList(`/admin/people?kind=${kind}`);
  const [form, setForm] = useState(null),
    [error, setError] = useState(""),
    [message, setMessage] = useState(""),
    [busy, setBusy] = useState(false);
  const canEdit = user?.is_admin || user?.role === "editor",
    author = kind === "author";
  async function save(event) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      const { id, name, email, institution, biography, active } = form;
      await request(`/admin/people${id ? `/${id}` : ""}`, {
        method: id ? "PATCH" : "POST",
        body: JSON.stringify({
          name,
          email,
          institution,
          biography,
          active,
          kind,
        }),
      });
      setForm(null);
      setMessage("Cadastro salvo.");
      list.refresh();
    } catch (error) {
      setError(error.message);
    } finally {
      setBusy(false);
    }
  }
  const newPerson = () => {
    setForm({
      name: "",
      email: "",
      institution: "",
      biography: "",
      active: true,
    });
    setError("");
    setMessage("");
  };
  return (
    <AdminLayout
      title={author ? "Autores" : "Pareceristas"}
      subtitle={
        author
          ? "Gerencie autores vinculados às edições da revista."
          : "Acompanhe os responsáveis pela revisão das publicações."
      }
      action={
        canEdit && (
          <button className="button primary" onClick={newPerson}>
            <Icon name="plus" />
            {author ? "Novo autor" : "Novo parecerista"}
          </button>
        )
      }
    >
      {message && <p role="status">{message}</p>}
      {error && <p role="alert">{error}</p>}
      {form && (
        <form
          className="admin-panel form-panel publication-form"
          onSubmit={save}
        >
          <h2>
            {form.id
              ? "Editar cadastro"
              : author
                ? "Novo autor"
                : "Novo parecerista"}
          </h2>
          <label>
            Nome
            <input
              required
              maxLength={200}
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
            />
          </label>
          <div>
            <label>
              E-mail profissional
              <input
                type="email"
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
              />
            </label>
            <label>
              Instituição
              <input
                maxLength={200}
                value={form.institution}
                onChange={(e) =>
                  setForm({ ...form, institution: e.target.value })
                }
              />
            </label>
          </div>
          <label>
            Biografia
            <textarea
              rows="3"
              value={form.biography}
              onChange={(e) => setForm({ ...form, biography: e.target.value })}
            />
          </label>
          <label className="check-label">
            <input
              type="checkbox"
              checked={form.active}
              onChange={(e) => setForm({ ...form, active: e.target.checked })}
            />
            Ativo para novos vínculos
          </label>
          <div className="form-actions">
            <button
              type="button"
              className="button secondary"
              onClick={() => setForm(null)}
            >
              Cancelar
            </button>
            <button className="button primary" disabled={busy}>
              Salvar cadastro
            </button>
          </div>
        </form>
      )}
      <ListControls list={list} />
      <section className="admin-panel simple-admin-list">
        {list.rows.map((person) => (
          <div key={person.id}>
            <div className="avatar">{person.name[0]}</div>
            <div>
              <strong>{person.name}</strong>
              <span>
                {person.count} publicações ·{" "}
                {person.active ? "Ativo" : "Inativo"}
                {person.institution ? ` · ${person.institution}` : ""}
              </span>
            </div>
            {canEdit && (
              <button
                onClick={() => {
                  setForm(person);
                  setError("");
                  setMessage("");
                }}
              >
                Editar
              </button>
            )}
          </div>
        ))}
      </section>
      <Pages list={list} />
    </AdminLayout>
  );
}
export function UsersAdmin() {
  const auth = useAuth(),
    list = useList("/admin/users");
  const [form, setForm] = useState(null),
    [error, setError] = useState(""),
    [message, setMessage] = useState(""),
    [busy, setBusy] = useState(false);
  async function save(event) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      const { id, email, name, role, is_active, password } = form;
      await request(`/admin/users${id ? `/${id}` : ""}`, {
        method: id ? "PATCH" : "POST",
        body: JSON.stringify({
          email,
          name,
          role,
          is_active,
          ...(password ? { password } : {}),
        }),
      });
      setForm(null);
      setMessage("Usuário salvo.");
      list.refresh();
      await auth.restore();
    } catch (error) {
      setError(error.message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <AdminLayout
      title="Usuários"
      subtitle="Controle quem pode administrar e publicar conteúdo."
      action={
        <button
          className="button primary"
          onClick={() => {
            setForm({
              email: "",
              name: "",
              role: "collaborator",
              is_active: true,
              password: "",
            });
            setError("");
            setMessage("");
          }}
        >
          <Icon name="plus" />
          Novo usuário
        </button>
      }
    >
      {error && <p role="alert">{error}</p>}
      {message && <p role="status">{message}</p>}
      {form && (
        <form
          className="admin-panel form-panel publication-form"
          onSubmit={save}
        >
          <h2>{form.id ? "Editar usuário" : "Novo usuário"}</h2>
          <label>
            Nome
            <input
              required
              value={form.name}
              maxLength={200}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
            />
          </label>
          <label>
            E-mail
            <input
              type="email"
              required
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
            />
          </label>
          <label>
            Perfil
            <select
              value={form.role}
              onChange={(e) => setForm({ ...form, role: e.target.value })}
            >
              <option value="admin">Administrador</option>
              <option value="editor">Editor</option>
              <option value="collaborator">Colaborador</option>
            </select>
          </label>
          <label>
            {form.id ? "Nova senha (opcional)" : "Senha inicial"}
            <input
              type="password"
              autoComplete="new-password"
              minLength={8}
              required={!form.id}
              value={form.password || ""}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
            />
          </label>
          <label className="check-label">
            <input
              type="checkbox"
              checked={form.is_active}
              onChange={(e) =>
                setForm({ ...form, is_active: e.target.checked })
              }
            />
            Usuário ativo
          </label>
          <div className="form-actions">
            <button
              type="button"
              className="button secondary"
              onClick={() => setForm(null)}
            >
              Cancelar
            </button>
            <button className="button primary" disabled={busy}>
              Salvar usuário
            </button>
          </div>
        </form>
      )}
      <ListControls list={list} />
      <section className="admin-panel simple-admin-list">
        {list.rows.map((user) => (
          <div key={user.id}>
            <div className="avatar">{user.name[0]}</div>
            <div>
              <strong>{user.name}</strong>
              <span>
                {user.email} · {user.role_label} ·{" "}
                {user.is_active ? "Ativo" : "Inativo"}
              </span>
            </div>
            <button
              onClick={() => {
                setForm({ ...user, password: "" });
                setError("");
                setMessage("");
              }}
            >
              Editar
            </button>
          </div>
        ))}
      </section>
      <Pages list={list} />
      <div className="permission-note">
        <strong>Permissões</strong>
        <p>
          Administrador gerencia acessos e configurações. Editor publica.
          Colaborador prepara seus rascunhos. O último administrador ativo é
          preservado.
        </p>
      </div>
    </AdminLayout>
  );
}
export function SettingsAdmin() {
  const { refresh } = useCatalog();
  const [form, setForm] = useState(null),
    [error, setError] = useState(""),
    [message, setMessage] = useState(""),
    [busy, setBusy] = useState(false),
    [attempt, setAttempt] = useState(0);
  useEffect(() => {
    const controller = new AbortController();
    request("/admin/settings", { signal: controller.signal })
      .then(setForm)
      .catch((error) => {
        if (!controller.signal.aborted) setError(error.message);
      });
    return () => controller.abort();
  }, [attempt]);
  async function save(event) {
    event.preventDefault();
    setBusy(true);
    setError("");
    setMessage("");
    try {
      const { updated_at: _updated, ...data } = form;
      setForm(
        await request("/admin/settings", {
          method: "PATCH",
          body: JSON.stringify(data),
        }),
      );
      setMessage("Configurações salvas.");
      refresh();
    } catch (error) {
      setError(error.message);
    } finally {
      setBusy(false);
    }
  }
  const input = (key, event) => setForm({ ...form, [key]: event.target.value });
  return (
    <AdminLayout
      title="Configurações"
      subtitle="Preferências institucionais e editoriais da plataforma."
    >
      {error && (
        <p role="alert">
          {error}
          {!form && (
            <button
              onClick={() => {
                setError("");
                setAttempt((n) => n + 1);
              }}
            >
              Tentar novamente
            </button>
          )}
        </p>
      )}
      {message && <p role="status">{message}</p>}
      {!form && !error && <p role="status">Carregando configurações…</p>}
      {form && (
        <form onSubmit={save}>
          <div className="settings-grid">
            <section className="admin-panel settings-card">
              <h2>Revista</h2>
              <label>
                Nome
                <input
                  required
                  maxLength={200}
                  value={form.name}
                  onChange={(e) => input("name", e)}
                />
              </label>
              <label>
                Descrição
                <textarea
                  rows="4"
                  value={form.description}
                  onChange={(e) => input("description", e)}
                />
              </label>
              <label>
                ISSN
                <input
                  value={form.issn}
                  maxLength={9}
                  placeholder="0000-0000"
                  onChange={(e) => input("issn", e)}
                />
              </label>
            </section>
            <section className="admin-panel settings-card">
              <h2>Recursos</h2>
              {[
                ["ratings_enabled", "Avaliações"],
                ["downloads_enabled", "Downloads"],
                ["public_archive_enabled", "Acervo público"],
              ].map(([key, label]) => (
                <button
                  type="button"
                  key={key}
                  className="toggle-row"
                  role="switch"
                  aria-checked={form[key]}
                  onClick={() => setForm({ ...form, [key]: !form[key] })}
                >
                  <span>{label}</span>
                  <i className={form[key] ? "on" : ""}>
                    <b />
                  </i>
                </button>
              ))}
            </section>
            <section className="admin-panel settings-card">
              <h2>Conteúdo institucional</h2>
              <label>
                Normas para autores
                <textarea
                  rows="5"
                  value={form.author_guidelines}
                  onChange={(e) => input("author_guidelines", e)}
                />
              </label>
              <label>
                Política editorial
                <textarea
                  rows="5"
                  value={form.editorial_policy}
                  onChange={(e) => input("editorial_policy", e)}
                />
              </label>
              <label>
                E-mail de contato
                <input
                  type="email"
                  value={form.contact_email}
                  onChange={(e) => input("contact_email", e)}
                />
              </label>
              <label>
                Informações de contato
                <textarea
                  rows="3"
                  value={form.contact_text}
                  onChange={(e) => input("contact_text", e)}
                />
              </label>
              <div className="settings-brand">
                <img src="/unieuro-logo.png" alt="Logo UNIEURO" />
                <span>Logo oficial do Centro Universitário UNIEURO</span>
              </div>
            </section>
          </div>
          <div className="form-actions">
            <button className="button primary" disabled={busy}>
              Salvar configurações
            </button>
          </div>
        </form>
      )}
    </AdminLayout>
  );
}
export function AuditAdmin() {
  const list = useList("/admin/audit");
  const actions = {
    "user.create": "Usuário criado",
    "user.update": "Acesso ou cadastro alterado",
    "person.create": "Cadastro editorial criado",
    "person.update": "Cadastro editorial alterado",
    "category.create": "Categoria criada",
    "category.update": "Categoria alterada",
    "settings.update": "Configurações alteradas",
    "publication.create": "Rascunho criado",
    "publication.update": "Edição alterada",
    "publication.publish": "Edição publicada",
    "publication.archive": "Edição arquivada",
    "publication.restore": "Rascunho restaurado",
    "document.upload": "PDF enviado",
    "document.cover": "Capa alterada",
  };
  const labels = {
    name: "Nome",
    email: "E-mail",
    role: "Perfil",
    is_active: "Acesso ativo",
    credential: "Senha",
    active: "Ativo",
    kind: "Tipo",
    institution: "Instituição",
    biography: "Biografia",
    category_ids: "Categorias",
    author_ids: "Autores",
    reviewer_ids: "Pareceristas",
    document: "PDF",
    title: "Título",
    issue: "Número da edição",
    publication_date: "Data",
    description: "Descrição",
    status: "Situação",
    file: "Arquivo",
    cover: "Capa",
    issn: "ISSN",
    ratings_enabled: "Avaliações",
    downloads_enabled: "Downloads",
    public_archive_enabled: "Acervo público",
    author_guidelines: "Normas",
    editorial_policy: "Política editorial",
    contact_email: "E-mail de contato",
    contact_text: "Contato",
    slug: "Endereço",
    position: "Ordem",
    icon: "Ícone",
  };
  return (
    <AdminLayout
      title="Histórico de alterações"
      subtitle="Acompanhe as alterações administrativas registradas pelo sistema."
    >
      {list.loading && <p role="status">Carregando histórico…</p>}
      {list.error && <p role="alert">{list.error}</p>}
      <section className="admin-panel table-scroll">
        <table>
          <thead>
            <tr>
              <th>Data</th>
              <th>Responsável</th>
              <th>Ação</th>
              <th>Registro</th>
              <th>Campos</th>
            </tr>
          </thead>
          <tbody>
            {list.rows.map((event) => (
              <tr key={event.id}>
                <td>{new Date(event.created_at).toLocaleString("pt-BR")}</td>
                <td>{event.actor_name}</td>
                <td>{actions[event.action] || "Alteração administrativa"}</td>
                <td>{event.target_label || "Registro editorial"}</td>
                <td>
                  {event.fields
                    .map((field) => labels[field] || field)
                    .join(", ") || "Cadastro"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {!list.loading && !list.rows.length && (
          <p>Nenhuma alteração registrada.</p>
        )}
      </section>
      <Pages list={list} />
    </AdminLayout>
  );
}
