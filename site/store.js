// The private layer: his own application status per program.
//
// This lives ONLY in localStorage. The site is a static file server — there is no backend,
// so privacy here is structural, not a policy. That matters because he's handing this URL to
// other people: there is nowhere for personal state to leak to, by construction.
//
// Cross-device sync is a URL *fragment* (`#/mine?d=...`). Fragments are never transmitted to
// the server by spec, so a sync link can go through iMessage/AirDrop without the payload
// touching GitHub.

const KEY = "radar.mine.v1";
const HIDE_KEY = "radar.personal.hidden";

export const STAGES = ["interested", "applied", "OA", "interview", "offer", "rejected", "passed"];
// Once he's applied, the row has done its job and should stop competing for attention.
export const DONE_STAGES = new Set(["applied", "OA", "interview", "offer", "rejected", "passed"]);

function read() {
  try { return JSON.parse(localStorage.getItem(KEY) || "{}"); } catch { return {}; }
}
function write(data) {
  localStorage.setItem(KEY, JSON.stringify(data));
  window.dispatchEvent(new CustomEvent("radar:mine"));
  return data;
}

export const all = () => read();
export const get = (id) => read()[id] || null;
export const isDone = (id) => { const e = get(id); return !!e && DONE_STAGES.has(e.stage); };

export function set(id, patch) {
  const data = read();
  const prev = data[id] || {};
  const next = { ...prev, ...patch, updated_at: new Date().toISOString() };
  if (patch.stage === "applied" && !prev.applied_at) next.applied_at = next.updated_at;
  data[id] = next;
  return write(data);
}

export function clearOne(id) {
  const data = read();
  delete data[id];
  return write(data);
}

/** One-click toggle. Deliberately not a form — friction is why his last log died. */
export function toggleApplied(id) {
  const cur = get(id);
  if (cur && cur.stage === "applied") return clearOne(id);
  return set(id, { stage: "applied" });
}

export function toggleStar(id) {
  const cur = get(id) || {};
  return set(id, { star: !cur.star });
}

export function counts() {
  const data = read();
  const vals = Object.values(data);
  return {
    total: vals.length,
    applied: vals.filter((v) => DONE_STAGES.has(v.stage)).length,
    starred: vals.filter((v) => v.star).length,
  };
}

// ---------------------------------------------------------------- screen-share guard
export const personalHidden = () => localStorage.getItem(HIDE_KEY) === "1";
export function togglePersonalHidden() {
  localStorage.setItem(HIDE_KEY, personalHidden() ? "0" : "1");
  window.dispatchEvent(new CustomEvent("radar:mine"));
  return personalHidden();
}

// ---------------------------------------------------------------- export / import / sync
export function exportBlob() {
  return new Blob([JSON.stringify({ v: 1, exported_at: new Date().toISOString(), mine: read() }, null, 2)],
                  { type: "application/json" });
}

export function importObject(obj, { merge = true } = {}) {
  const incoming = obj && obj.mine ? obj.mine : obj;
  if (!incoming || typeof incoming !== "object") throw new Error("not a radar export");
  const data = merge ? read() : {};
  let changed = 0;
  for (const [id, entry] of Object.entries(incoming)) {
    const cur = data[id];
    // Last write wins per program, so importing an older phone export can't clobber newer edits.
    if (!cur || (entry.updated_at || "") > (cur.updated_at || "")) { data[id] = entry; changed++; }
  }
  write(data);
  return changed;
}

const b64 = {
  enc: (s) => btoa(String.fromCharCode(...new TextEncoder().encode(s)))
    .replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, ""),
  dec: (s) => new TextDecoder().decode(Uint8Array.from(
    atob(s.replace(/-/g, "+").replace(/_/g, "/")), (c) => c.charCodeAt(0))),
};

export const encodeSync = () => b64.enc(JSON.stringify(read()));
export const decodeSync = (s) => JSON.parse(b64.dec(s));

export function syncLink() {
  return `${location.origin}${location.pathname}#/mine?d=${encodeSync()}`;
}
