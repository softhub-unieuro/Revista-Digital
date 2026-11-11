import { useState } from "react";
import { AdminLayout } from "./admin-layout";
import { useAuth } from "./auth";
import { useCatalog } from "./catalog";
import { request } from "./api";
import { Icon } from "./ui";
const initial = {
  name: "",
  slug: "",
  icon: "brain",
  position: 0,
  active: true,
};
export function CategoriesAdmin() {
  const { adminCategories, refresh, adminError } = useCatalog(),
    { user } = useAuth();
  const [form, setForm] = useState(null),
    [error, setError] = useState(""),
    [message, setMessage] = useState(""),
    [busy, setBusy] = useState(false);
  const edit = ["admin", "editor"].includes(user?.role);
  async function save(event) {
    event.preventDefault();
    setBusy(true);
    setError("");
    setMessage("");
    try {
      const { id, ...data } = form;
      await request(`/admin/categories${id ? `/${id}` : ""}`, {
        method: id ? "PATCH" : "POST",
        body: JSON.stringify(data),
      });
      setForm(null);
      refresh();
      setMessage("Categoria salva.");
    } catch (error) {
      setError(error.message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <AdminLayout
      title="Categorias"
      subtitle="Organize as publicações por áreas da Psicologia."
      action={
        edit && (
          <button
            className="button primary"
            onClick={() => {
              setForm(initial);
              setError("");
            }}
          >
            <Icon name="plus" />
            Nova categoria
          </button>
        )
      }
    >
      {(error || adminError) && (
        <p className="action-feedback action-feedback--error" role="alert">
          {error || adminError}
        </p>
      )}
      {message && (
        <p className="action-feedback action-feedback--success" role="status">
          {message}
        </p>
      )}
      {form && (
        <form
          className="admin-panel form-panel publication-form"
          onSubmit={save}
        >
          <h2>{form.id ? "Editar categoria" : "Nova categoria"}</h2>
          <label>
            Nome da categoria
            <input
              required
              maxLength={100}
              value={form.name}
              onChange={(e) =>
                setForm({
                  ...form,
                  name: e.target.value,
                  ...(!form.id
                    ? {
                        slug: e.target.value
                          .normalize("NFD")
                          .replace(/[\u0300-\u036f]/g, "")
                          .toLowerCase()
                          .replace(/[^a-z0-9]+/g, "-")
                          .replace(/^-|-$/g, ""),
                      }
                    : {}),
                })
              }
            />
          </label>
          <label>
            Endereço do tema
            <input
              required
              pattern="[a-z0-9_-]+"
              value={form.slug}
              onChange={(e) => setForm({ ...form, slug: e.target.value })}
            />
          </label>
          <label>
            Ícone
            <select
              value={form.icon}
              onChange={(e) => setForm({ ...form, icon: e.target.value })}
            >
              {["brain", "school", "family", "network", "leaf", "nodes"].map(
                (icon) => (
                  <option key={icon}>{icon}</option>
                ),
              )}
            </select>
          </label>
          <label>
            Ordem
            <input
              type="number"
              min="0"
              value={form.position}
              onChange={(e) =>
                setForm({ ...form, position: Number(e.target.value) })
              }
            />
          </label>
          <label>
            <input
              type="checkbox"
              checked={form.active}
              onChange={(e) => setForm({ ...form, active: e.target.checked })}
            />
            Tema ativo na navegação pública
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
              Salvar categoria
            </button>
          </div>
        </form>
      )}
      <section className="admin-panel simple-admin-list">
        {adminCategories.map((c) => (
          <div key={c.id}>
            <Icon name={c.icon} />
            <div>
              <strong>{c.name}</strong>
              <span>
                {c.count} publicações{!c.active ? " · Inativo" : ""}
              </span>
            </div>
            {edit && (
              <button
                onClick={() => {
                  setForm(c);
                  setError("");
                }}
              >
                Editar
              </button>
            )}
          </div>
        ))}
      </section>
    </AdminLayout>
  );
}
