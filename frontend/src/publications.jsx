import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { AdminLayout } from "./admin-layout";
import { request } from "./api";
import { useAuth } from "./auth";
import { useCatalog, editionFromApi, all } from "./catalog";
import { Cover, Icon } from "./ui";
import { publicationToday } from "./editorial-date";
const versionHeaders = (row) => ({
  "If-Match": `"${row.id}:${row.edit_version}"`,
});
const empty = () => ({
  title: "",
  issue: "",
  publication_date: publicationToday(),
  description: "",
  category_ids: [],
  author_ids: [],
  reviewer_ids: [],
});
export function PublicationForm({ value, onChange, categories }) {
  const [people, setPeople] = useState([]),
    [peopleError, setPeopleError] = useState(""),
    [attempt, setAttempt] = useState(0);
  useEffect(() => {
    const controller = new AbortController();
    all("/admin/people", controller.signal)
      .then(setPeople)
      .catch((error) => {
        if (!controller.signal.aborted) setPeopleError(error.message);
      });
    return () => controller.abort();
  }, [attempt]);

  const field = (name, event) =>
    onChange({ ...value, [name]: event.target.value });
  return (
    <div className="publication-form">
      <h2>Informações da edição</h2>
      <label>
        Título
        <input
          required
          maxLength={255}
          value={value.title}
          onChange={(e) => field("title", e)}
        />
      </label>
      <div>
        <label>
          Número da edição
          <input
            required
            maxLength={50}
            value={value.issue}
            onChange={(e) => field("issue", e)}
            placeholder="N. 13"
          />
        </label>
        <label>
          Data da publicação
          <input
            required
            type="date"
            value={value.publication_date}
            onChange={(e) => field("publication_date", e)}
          />
        </label>
      </div>
      <label>
        Descrição
        <textarea
          rows="4"
          value={value.description}
          onChange={(e) => field("description", e)}
        />
      </label>
      <fieldset>
        <legend>Categorias</legend>
        <div className="category-options">
          {categories
            .filter((c) => c.active || value.category_ids.includes(c.id))
            .map((c) => (
              <label key={c.id}>
                <input
                  type="checkbox"
                  checked={value.category_ids.includes(c.id)}
                  onChange={(e) =>
                    onChange({
                      ...value,
                      category_ids: e.target.checked
                        ? [...value.category_ids, c.id]
                        : value.category_ids.filter((id) => id !== c.id),
                    })
                  }
                />
                {c.name}
              </label>
            ))}
        </div>
      </fieldset>
      {peopleError && (
        <p role="alert">
          {peopleError}
          <button
            type="button"
            onClick={() => {
              setPeopleError("");
              setAttempt((n) => n + 1);
            }}
          >
            Tentar novamente
          </button>
        </p>
      )}
      {[
        ["author_ids", "author", "Autores"],
        ["reviewer_ids", "reviewer", "Pareceristas"],
      ].map(([key, kind, label]) => (
        <fieldset key={key}>
          <legend>{label}</legend>
          <div className="category-options">
            {people
              .filter(
                (p) =>
                  p.kind === kind && (p.active || value[key]?.includes(p.id)),
              )
              .map((p) => (
                <label key={p.id}>
                  <input
                    type="checkbox"
                    checked={value[key]?.includes(p.id) || false}
                    onChange={(e) =>
                      onChange({
                        ...value,
                        [key]: e.target.checked
                          ? [...(value[key] || []), p.id]
                          : (value[key] || []).filter((id) => id !== p.id),
                      })
                    }
                  />
                  {p.name}
                  {!p.active ? " (Inativo)" : ""}
                </label>
              ))}
            {!people.some((p) => p.kind === kind) && !peopleError && (
              <small>Nenhum cadastro disponível. O vínculo é opcional.</small>
            )}
          </div>
        </fieldset>
      ))}
    </div>
  );
}
function valid(value) {
  return (
    value.title.trim() &&
    value.issue.trim() &&
    value.publication_date &&
    value.category_ids.length
  );
}
function Upload({ doc, onChange }) {
  const [busy, setBusy] = useState(false),
    [error, setError] = useState(""),
    [poll, setPoll] = useState(0);
  useEffect(() => {
    if (!doc || !["queued", "processing"].includes(doc.state)) return;
    const controller = new AbortController();
    const timer = setTimeout(
      () =>
        request(`/admin/jobs/${doc.id}`, { signal: controller.signal })
          .then(onChange)
          .catch((error) => {
            if (!controller.signal.aborted) setError(error.message);
          }),
      1200,
    );
    return () => {
      clearTimeout(timer);
      controller.abort();
    };
  }, [doc, onChange, poll]);
  async function upload(file) {
    if (!file) return;
    setError("");
    if (file.size > 200 * 1024 * 1024) {
      setError("O tamanho máximo permitido é 200 MiB.");
      return;
    }
    setBusy(true);
    try {
      const body = new FormData();
      body.append("file", file);
      onChange(await request("/admin/uploads", { method: "POST", body }));
    } catch (error) {
      if (error.data?.id) onChange(error.data);
      setError(error.message);
    } finally {
      setBusy(false);
    }
  }
  async function retry() {
    setError("");
    setBusy(true);
    try {
      onChange(
        await request(`/admin/jobs/${doc.id}/retry`, { method: "POST" }),
      );
      setPoll((n) => n + 1);
    } catch (error) {
      setError(error.message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <>
      <label
        className="dropzone"
        onDragOver={(e) => e.preventDefault()}
        onDrop={(e) => {
          e.preventDefault();
          if (!busy) upload(e.dataTransfer.files[0]);
        }}
      >
        <Icon name="upload" size={32} />
        <strong>{busy ? "Enviando PDF…" : "Arraste o PDF aqui"}</strong>
        <span>ou clique para selecionar · até 300 páginas e 200 MiB</span>
        <input
          aria-label="Arquivo PDF"
          type="file"
          accept="application/pdf,.pdf"
          disabled={busy}
          onChange={(e) => upload(e.target.files[0])}
        />
      </label>
      {doc && (
        <div
          className="upload-status"
          role={doc.state === "failed" ? "alert" : "status"}
        >
          <strong>{doc.original_name}</strong>
          <p>
            {
              {
                queued: "Aguardando processamento…",
                processing: "Validando PDF e preparando capa…",
                ready: `PDF pronto: ${doc.page_count} páginas.`,
                failed: doc.error_message,
              }[doc.state]
            }
          </p>
          {(doc.state === "failed" || (doc.state === "queued" && error)) && (
            <button
              type="button"
              className="button secondary"
              onClick={retry}
              disabled={busy}
            >
              Tentar processamento novamente
            </button>
          )}
        </div>
      )}
      {error && (
        <div className="upload-status" role="alert">
          {error}
          {doc && (
            <button
              type="button"
              className="text-button"
              onClick={() => {
                setError("");
                setPoll((n) => n + 1);
              }}
            >
              Consultar novamente
            </button>
          )}
        </div>
      )}
    </>
  );
}
function CoverPicker({ doc, onChange }) {
  const [error, setError] = useState(""),
    [busy, setBusy] = useState(false);
  async function cover(file, reset = false) {
    if (!file && !reset) return;
    setBusy(true);
    setError("");
    try {
      const body = new FormData();
      if (file) body.append("file", file);
      else body.append("reset", "true");
      onChange(
        await request(`/admin/jobs/${doc.id}/cover`, { method: "POST", body }),
      );
    } catch (error) {
      setError(error.message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <>
      <h2>Capa da revista</h2>
      <p>
        A primeira página do PDF é usada como capa. Você também pode enviar uma
        imagem.
      </p>
      <div className="cover-picker">
        <img
          className="cover"
          src={`${doc.cover_url}&v=${doc.cover_version || 0}`}
          alt="Capa da publicação"
        />
        <div>
          <button
            type="button"
            className="button secondary"
            disabled={busy}
            onClick={() => cover(null, true)}
          >
            Usar primeira página
          </button>
          <label className="text-button">
            Enviar outra imagem
            <input
              aria-label="Imagem da capa"
              type="file"
              accept="image/jpeg,image/png"
              disabled={busy}
              onChange={(e) => cover(e.target.files[0])}
            />
          </label>
        </div>
      </div>
      {error && <p role="alert">{error}</p>}
    </>
  );
}
export function NewPublication() {
  const [clientKey] = useState(() => crypto.randomUUID());
  const [step, setStep] = useState(1),
    [doc, setDoc] = useState(null),
    [value, setValue] = useState(empty),
    [error, setError] = useState(""),
    [busy, setBusy] = useState(false),
    [saved, setSaved] = useState(null);
  const { adminCategories, refresh } = useCatalog(),
    { user } = useAuth(),
    navigate = useNavigate();
  const publisher = ["admin", "editor"].includes(user?.role);
  async function finish(publish) {
    setError("");
    setBusy(true);
    try {
      let row = saved;
      if (!row) {
        row = await request("/admin/publications", {
          method: "POST",
          body: JSON.stringify({
            ...value,
            document_id: doc.id,
            client_key: clientKey,
          }),
        });
        setSaved(row);
      }
      const changed =
        row.document_version !== doc.id ||
        Object.entries(value).some(
          ([key, field]) =>
            JSON.stringify(field) !==
            JSON.stringify(
              key === "category_ids"
                ? row.categories.map((category) => category.id)
                : key === "author_ids"
                  ? row.authors.map((person) => person.id)
                  : key === "reviewer_ids"
                    ? row.reviewers.map((person) => person.id)
                    : row[key],
            ),
        );
      if (changed)
        row = await request(`/admin/publications/${row.id}`, {
          method: "PATCH",
          headers: versionHeaders(row),
          body: JSON.stringify({ ...value, document_id: doc.id }),
        });
      setSaved(row);
      if (publish)
        await request(`/admin/publications/${row.id}/publish`, {
          method: "POST",
          headers: versionHeaders(row),
        });
      refresh();
      navigate(`/admin/publicacoes/${row.id}`, {
        state: { message: publish ? "Edição publicada." : "Rascunho salvo." },
      });
    } catch (error) {
      setError(error.message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <AdminLayout
      title="Nova publicação"
      subtitle="Cadastre uma nova edição em quatro etapas simples."
    >
      <div className="wizard">
        <div className="stepper">
          {["Arquivo", "Informações", "Capa", "Revisão"].map((label, i) => (
            <div className={step >= i + 1 ? "active" : ""} key={label}>
              <b>{i + 1}</b>
              <span>{label}</span>
            </div>
          ))}
        </div>
        <section className="wizard-panel">
          {step === 1 && (
            <>
              <h2>Envie a revista</h2>
              <p>
                Selecione o PDF final. O sistema identificará a quantidade de
                páginas e preparará a visualização.
              </p>
              <Upload doc={doc} onChange={setDoc} />
            </>
          )}
          {step === 2 && (
            <PublicationForm
              value={value}
              onChange={setValue}
              categories={adminCategories}
            />
          )}
          {step === 3 && <CoverPicker doc={doc} onChange={setDoc} />}
          {step === 4 && (
            <>
              <h2>Revisar publicação</h2>
              <div className="review-grid">
                <img className="cover" src={doc.cover_url} alt="Capa" />
                <dl>
                  <div>
                    <dt>Título</dt>
                    <dd>{value.title}</dd>
                  </div>
                  <div>
                    <dt>Edição</dt>
                    <dd>
                      {value.issue} · {value.publication_date}
                    </dd>
                  </div>
                  <div>
                    <dt>Páginas</dt>
                    <dd>{doc.page_count}</dd>
                  </div>
                  <div>
                    <dt>Categorias</dt>
                    <dd>
                      {adminCategories
                        .filter((c) => value.category_ids.includes(c.id))
                        .map((c) => c.name)
                        .join(" · ")}
                    </dd>
                  </div>
                </dl>
              </div>
            </>
          )}
          {error && (
            <p role="alert" className="form-error">
              {error}
            </p>
          )}
          <div className="wizard-buttons">
            {step > 1 && (
              <button
                disabled={busy}
                className="button secondary"
                onClick={() => setStep((n) => n - 1)}
              >
                Voltar
              </button>
            )}
            {step < 4 ? (
              <button
                className="button primary"
                disabled={
                  (step === 1 && doc?.state !== "ready") ||
                  (step === 2 && !valid(value))
                }
                onClick={() => setStep((n) => n + 1)}
              >
                Continuar
              </button>
            ) : (
              <>
                <button
                  disabled={busy}
                  className="button secondary"
                  onClick={() => finish(false)}
                >
                  Salvar rascunho
                </button>
                {publisher && (
                  <button
                    disabled={busy}
                    className="button primary"
                    onClick={() => finish(true)}
                  >
                    {busy ? "Salvando…" : "Publicar edição"}
                  </button>
                )}
              </>
            )}
          </div>
        </section>
      </div>
    </AdminLayout>
  );
}
function RevisionHistory({ id }) {
  const [open, setOpen] = useState(false),
    [rows, setRows] = useState([]),
    [error, setError] = useState("");
  useEffect(() => {
    if (!open) return;
    const controller = new AbortController();
    all(`/admin/publications/${id}/revisions`, controller.signal)
      .then(setRows)
      .catch((error) => {
        if (!controller.signal.aborted) setError(error.message);
      });
    return () => controller.abort();
  }, [id, open]);
  return (
    <details
      className="revision-history"
      onToggle={(event) => setOpen(event.currentTarget.open)}
    >
      <summary>Histórico de arquivos</summary>
      {error && <p role="alert">{error}</p>}
      {open &&
        rows.map((revision) => (
          <div key={revision.id}>
            <strong>{revision.snapshot.title}</strong>
            <small>
              {new Date(revision.created_at).toLocaleString("pt-BR")} ·{" "}
              {revision.page_count} páginas
            </small>
            <Link to={revision.preview_url}>Ler arquivo desta versão</Link>
          </div>
        ))}
      {open && !rows.length && !error && (
        <p>Sem versões anteriores registradas.</p>
      )}
    </details>
  );
}

export function EditPublication() {
  const { id } = useParams(),
    { user } = useAuth(),
    { adminCategories, refresh } = useCatalog();
  const [row, setRow] = useState(null),
    [value, setValue] = useState(empty),
    [doc, setDoc] = useState(null),
    [error, setError] = useState(""),
    [message, setMessage] = useState(""),
    [busy, setBusy] = useState(false);
  const [loadVersion, setLoadVersion] = useState(0);
  const [conflict, setConflict] = useState(false);
  useEffect(() => {
    if (!user) return;
    const controller = new AbortController();
    setError("");
    setRow(null);
    request(`/admin/publications/${id}`, { signal: controller.signal })
      .then((row) => {
        if (controller.signal.aborted) return;
        setConflict(false);
        setDoc(null);
        setRow(row);
        setValue({
          ...row,
          category_ids: row.categories.map((c) => c.id),
          author_ids: row.authors.map((p) => p.id),
          reviewer_ids: row.reviewers.map((p) => p.id),
        });
      })
      .catch((error) => {
        if (!controller.signal.aborted) setError(error.message);
      });
    return () => controller.abort();
  }, [id, user, loadVersion]);
  const publisher = ["admin", "editor"].includes(user?.role);
  async function save(action) {
    setBusy(true);
    setError("");
    setMessage("");
    try {
      let updated = await request(`/admin/publications/${id}`, {
        method: "PATCH",
        headers: versionHeaders(row),
        body: JSON.stringify({
          title: value.title,
          issue: value.issue,
          publication_date: value.publication_date,
          description: value.description,
          category_ids: value.category_ids,
          author_ids: value.author_ids,
          reviewer_ids: value.reviewer_ids,
          ...(doc ? { document_id: doc.id } : {}),
        }),
      });
      setRow(updated);
      if (action)
        updated = await request(`/admin/publications/${id}/${action}`, {
          method: "POST",
          headers: versionHeaders(updated),
        });
      setRow(updated);
      refresh();
      setDoc(null);
      setMessage("Alterações salvas.");
    } catch (error) {
      if (error.status === 412) setConflict(true);
      setError(error.message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <AdminLayout
      title="Editar publicação"
      subtitle={row ? `${row.issue} · ${row.title}` : "Carregando edição…"}
    >
      {error && (
        <p role="alert" className="form-error">
          {error}
          {conflict && (
            <>
              <span>
                {" "}
                Seu formulário foi mantido. Copie os textos que deseja preservar
                antes de carregar os dados atuais.
              </span>
              <button
                className="text-button"
                onClick={() => setLoadVersion((n) => n + 1)}
              >
                Carregar versão atual
              </button>
            </>
          )}
          {!row && (
            <button
              className="text-button"
              onClick={() => setLoadVersion((n) => n + 1)}
            >
              Tentar novamente
            </button>
          )}
        </p>
      )}
      {message && <p role="status">{message}</p>}
      {row && (
        <div className="edit-grid">
          <section className="admin-panel form-panel">
            <fieldset
              className="editor-fields"
              disabled={!publisher && row.status !== "draft"}
            >
              <PublicationForm
                value={value}
                onChange={setValue}
                categories={adminCategories}
              />
              {(publisher || row.status === "draft") && (
                <details>
                  <summary>Substituir PDF</summary>
                  <p>
                    O arquivo atual continua disponível até você salvar o novo
                    PDF processado.
                  </p>
                  <Upload doc={doc} onChange={setDoc} />
                </details>
              )}
              <div className="form-actions">
                <button
                  disabled={
                    busy ||
                    conflict ||
                    !valid(value) ||
                    (!!doc && doc.state !== "ready")
                  }
                  className="button primary"
                  onClick={() => save()}
                >
                  Salvar alterações
                </button>
                {publisher && (
                  <button
                    disabled={
                      busy ||
                      conflict ||
                      !valid(value) ||
                      (!!doc && doc.state !== "ready")
                    }
                    className="button secondary"
                    onClick={() =>
                      save(
                        row.status === "published"
                          ? "archive"
                          : row.status === "archived"
                            ? "restore"
                            : "publish",
                      )
                    }
                  >
                    {
                      {
                        published: "Arquivar",
                        archived: "Restaurar rascunho",
                        draft: "Publicar edição",
                      }[row.status]
                    }
                  </button>
                )}
              </div>
            </fieldset>
            {!publisher && row.status !== "draft" && (
              <p>Somente editores podem alterar esta edição.</p>
            )}
          </section>
          <aside className="admin-panel publication-preview">
            <Cover edition={editionFromApi(row)} />
            <p>
              {row.page_count} páginas · {editionFromApi(row).status}
            </p>
            <Link
              className="button secondary full"
              to={`/ler/${row.slug}?preview=${row.id}`}
            >
              Visualizar PDF
            </Link>
            {row.status === "published" && (
              <Link
                className="button secondary full"
                to={`/edicoes/${row.slug}`}
              >
                Ver no acervo
              </Link>
            )}
            <RevisionHistory key={row.updated_at} id={row.id} />
          </aside>
        </div>
      )}
    </AdminLayout>
  );
}
