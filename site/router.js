// Hash router, same shape as the kalshi desk's. Routes own their cleanup so polling timers
// from a page you navigated away from can never keep firing.

const routes = new Map();
let current = null;

export function route(path, render, label) {
  routes.set(path, { render, label });
}

export function routeList() {
  return [...routes.entries()].map(([path, r]) => ({ path, label: r.label }));
}

/** `#/board?sec=energy&loc=hou` -> { path: '/board', params: URLSearchParams } */
export function parseHash(hash = location.hash) {
  const raw = (hash || "").replace(/^#/, "") || "/board";
  const [path, query = ""] = raw.split("?");
  return { path: path || "/board", params: new URLSearchParams(query) };
}

/** Update the query string in place without adding a history entry per keystroke. */
export function setParams(params, { replace = true } = {}) {
  const { path } = parseHash();
  const qs = params.toString();
  const next = `#${path}${qs ? "?" + qs : ""}`;
  if (replace) history.replaceState(null, "", next);
  else location.hash = next;
  window.dispatchEvent(new CustomEvent("radar:params", { detail: { path, params } }));
}

export function start(mount, onBefore) {
  async function go() {
    const { path, params } = parseHash();
    const entry = routes.get(path) || routes.get("/board");
    if (current && current.cleanup) current.cleanup();
    current = null;
    onBefore?.(path);
    const cleanup = await entry.render(mount, params);
    current = { path, cleanup: typeof cleanup === "function" ? cleanup : null };
  }
  window.addEventListener("hashchange", go);
  window.addEventListener("radar:params", () => {
    // Re-render in place on filter changes; hashchange doesn't fire for replaceState.
    const { path } = parseHash();
    if (current && current.path === path) go();
  });
  go();
}
