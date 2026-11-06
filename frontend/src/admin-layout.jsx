import { Link as RouterLink } from "react-router-dom";
import { useState } from "react";
import { Link, NavLink } from "react-router-dom";
import { RequireAuth, useAuth } from "./auth";
import { Brand, Icon } from "./ui";
const adminNav = [
  ["grid", "Painel", "/admin"],
  ["file", "Edições", "/admin/publicacoes"],
  ["plus", "Nova publicação", "/admin/publicacoes/nova"],
  ["folder", "Categorias", "/admin/categorias"],
  ["users", "Autores", "/admin/autores"],
  ["users", "Pareceristas", "/admin/pareceristas"],
  ["users", "Usuários", "/admin/usuarios"],
  ["settings", "Configurações", "/admin/configuracoes"],
];
export function AdminLayout(props) {
  return (
    <RequireAuth>
      <AdminShell {...props} />
    </RequireAuth>
  );
}
function AdminShell({ title, subtitle, children, action }) {
  const { user, signOut } = useAuth();
  const [logoutError, setLogoutError] = useState("");
  return (
    <div className="admin-app">
      <header className="admin-topbar">
        <Brand compact />
        <div className="admin-topbar-actions">
          {user.is_admin && (
            <RouterLink
              className="admin-bell"
              to="/admin/auditoria"
              aria-label="Histórico de alterações"
            >
              <Icon name="file" size={18} />
            </RouterLink>
          )}
          <div className="admin-account">
            <div className="admin-avatar">
              {user.name?.[0] || user.email[0]}
            </div>
            <span>
              <b>{user.name || user.email}</b>
              <small>{user.role_label}</small>
            </span>
            <button
              className="account-logout"
              onClick={() =>
                signOut().catch(() =>
                  setLogoutError("Não foi possível sair. Tente novamente."),
                )
              }
            >
              Sair
            </button>
            {logoutError && <span role="alert">{logoutError}</span>}
          </div>
        </div>
      </header>
      <div className="admin-body">
        <aside className="admin-sidebar">
          <nav>
            {adminNav
              .filter(
                ([, , to]) =>
                  user.is_admin ||
                  !["/admin/usuarios", "/admin/configuracoes"].includes(to),
              )
              .map(([icon, label, to]) => (
                <NavLink end={to === "/admin"} key={to} to={to}>
                  <Icon name={icon} size={18} />
                  <span>{label}</span>
                </NavLink>
              ))}
          </nav>
        </aside>
        <main className="admin-main">
          <section className="admin-title-row">
            <div>
              <h1>{title}</h1>
              <p>{subtitle}</p>
            </div>
            {action && <div className="admin-title-action">{action}</div>}
          </section>
          <div className="admin-content">{children}</div>
        </main>
      </div>
    </div>
  );
}
