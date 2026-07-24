// DOM helpers. `el()` builds with createElement + textContent — NEVER innerHTML with data.
// Firm names, program titles and job URLs are third-party strings rendered on a public page;
// this is the one discipline that keeps a scraped title from becoming script injection.

export function el(tag, attrs = {}, ...kids) {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (v == null || v === false) continue;
    if (k === "class") node.className = v;
    else if (k === "text") node.textContent = v;
    else if (k === "html") throw new Error("el(): refusing to set innerHTML");
    else if (k.startsWith("on") && typeof v === "function") node.addEventListener(k.slice(2), v);
    else if (v === true) node.setAttribute(k, "");
    else node.setAttribute(k, String(v));
  }
  for (const kid of kids.flat()) {
    if (kid == null || kid === false) continue;
    node.append(kid instanceof Node ? kid : document.createTextNode(String(kid)));
  }
  return node;
}

export function frag(...kids) {
  const f = document.createDocumentFragment();
  for (const k of kids.flat()) if (k != null && k !== false) f.append(k);
  return f;
}

export function clear(node) {
  while (node.firstChild) node.removeChild(node.firstChild);
  return node;
}

/** "4 min ago" / "2h ago" / "3d ago" — the header clock is the truth, not the cron schedule. */
export function ago(iso, now = Date.now()) {
  if (!iso) return "never";
  const secs = Math.max(0, (now - Date.parse(iso)) / 1000);
  if (secs < 90) return `${Math.round(secs)}s ago`;
  const mins = secs / 60;
  if (mins < 90) return `${Math.round(mins)} min ago`;
  const hrs = mins / 60;
  if (hrs < 36) return `${Math.round(hrs)}h ago`;
  return `${Math.round(hrs / 24)}d ago`;
}

/** Countdown text. Deliberately vague for vague windows — see `precision`. */
export function untilText(days, precision) {
  if (days === 0) return "window open";
  if (days < 0) return "window passed";
  if (days > 900) return "unscheduled";
  const approx = precision === "season" || precision === "unknown" ? "~" : "";
  if (days === 1) return `${approx}1 day`;
  if (days < 45) return `${approx}${days} days`;
  return `${approx}${Math.round(days / 7)} wks`;
}

export function plural(n, one, many = one + "s") {
  return `${n} ${n === 1 ? one : many}`;
}
