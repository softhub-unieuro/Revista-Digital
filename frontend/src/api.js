let csrfToken;
export async function request(path, options = {}) {
  const method = options.method || "GET";
  if (!["GET", "HEAD"].includes(method) && !csrfToken) {
    const response = await fetch("/api/v1/auth/csrf", {
      credentials: "same-origin",
    });
    if (!response.ok)
      throw new Error("Não foi possível iniciar o acesso. Tente novamente.");
    csrfToken = (await response.json()).csrf_token;
  }
  const headers = { Accept: "application/json", ...options.headers };
  if (options.body && !(options.body instanceof FormData))
    headers["Content-Type"] = "application/json";
  if (!["GET", "HEAD"].includes(method)) headers["X-CSRFToken"] = csrfToken;
  const response = await fetch("/api/v1" + path, {
    ...options,
    method,
    credentials: "same-origin",
    headers,
  });
  const jsonResponse = response.headers
    .get("Content-Type")
    ?.includes("application/json");
  const data =
    response.status === 204 || !jsonResponse ? null : await response.json();
  if (!response.ok) {
    if (response.status === 403 || response.status === 401)
      csrfToken = undefined;
    if (response.status === 401 && path.startsWith("/admin/"))
      window.dispatchEvent(new Event("session-expired"));
    const error = new Error(
      data?.detail ||
        (data &&
          Object.entries(data)
            .map(
              ([key, value]) =>
                `${key}: ${Array.isArray(value) ? value.join(" ") : value}`,
            )
            .join(" ")) ||
        "Não foi possível concluir a operação.",
    );
    error.data = data;
    error.status = response.status;
    throw error;
  }
  if (path === "/auth/login" || path === "/auth/logout") csrfToken = undefined;
  return data;
}
