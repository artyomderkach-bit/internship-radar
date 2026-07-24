// Data access.
//
// The GitHub Pages gotcha this exists to solve: Pages sits behind a Fastly CDN that serves
// `max-age=600`. `cache: 'no-store'` defeats the *browser* cache but NOT the CDN, so without
// a cache-busting query param he'd see up-to-10-minute-stale data on a 30-minute tracker.
// Hence `?t=<epoch>` on every request.
//
// getJSON returns null on failure rather than throwing, so a page renders a visible
// placeholder instead of a blank screen when the network is down.

const BASE = "data";

export async function getJSON(name) {
  try {
    const res = await fetch(`${BASE}/${name}?t=${Date.now()}`, { cache: "no-store" });
    if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
    return await res.json();
  } catch (err) {
    console.warn(`[api] ${name}:`, err.message);
    return null;
  }
}

let boardCache = null;
let boardStamp = null;

/** Fetch meta (tiny) and only refetch the ~120 KB board when generated_at actually moved. */
export async function getBoard({ force = false } = {}) {
  const meta = await getJSON("meta.json");
  if (!force && meta && boardCache && meta.generated_at === boardStamp) {
    return { board: boardCache, meta, changed: false };
  }
  const board = await getJSON("board.json");
  if (board) {
    boardCache = board;
    boardStamp = board.meta?.generated_at ?? null;
  }
  return { board: board ?? boardCache, meta: meta ?? board?.meta ?? null, changed: true };
}

export const getEvents = () => getJSON("events.json");
