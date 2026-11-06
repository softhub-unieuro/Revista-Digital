import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react";
import { Link, Navigate, useLocation } from "react-router-dom";
import { request } from "./api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [state, setState] = useState({ ready: false, user: null, error: "" });
  const restore = useCallback(async () => {
    try {
      const data = await request("/auth/me");
      setState({ ready: true, user: data.user, error: "" });
    } catch {
      setState({
        ready: true,
        user: null,
        error: "O serviço de acesso está indisponível.",
      });
    }
  }, []);
  useEffect(() => {
    restore();
  }, [restore]);
  useEffect(() => {
    const expired = () => setState({ ready: true, user: null, error: "" });
    window.addEventListener("session-expired", expired);
    return () => window.removeEventListener("session-expired", expired);
  }, []);
  async function signIn(email, password) {
    const data = await request("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
    setState({ ready: true, user: data.user, error: "" });
  }
  async function signOut() {
    await request("/auth/logout", { method: "POST" });
    setState({ ready: true, user: null, error: "" });
  }
  return (
    <AuthContext.Provider value={{ ...state, signIn, signOut, restore }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}

export function RequireAuth({ children, roles }) {
  const auth = useAuth();
  const location = useLocation();
  if (!auth.ready)
    return (
      <p role="status" className="access-message">
        Verificando acesso…
      </p>
    );
  if (auth.error)
    return (
      <div className="access-message" role="alert">
        <p>{auth.error}</p>
        <button className="button secondary" onClick={auth.restore}>
          Tentar novamente
        </button>
      </div>
    );
  if (!auth.user)
    return (
      <Navigate
        to="/admin/login"
        replace
        state={{ from: location.pathname + location.search }}
      />
    );
  if (roles && !auth.user.is_admin && !roles.includes(auth.user.role))
    return (
      <main className="access-message">
        <h1>Acesso restrito</h1>
        <p>Seu perfil não permite acessar esta área.</p>
        <Link to="/admin">Voltar ao painel</Link>
      </main>
    );
  return children;
}
