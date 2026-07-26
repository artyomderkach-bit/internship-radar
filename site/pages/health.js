import { el, clear, ago } from "../render/fmt.js";
import { getBoard } from "../api.js";

export async function render(mount) {
  clear(mount);
  const { board } = await getBoard();
  if (!board) { mount.append(el("div", { class: "page-loading", text: "Could not load data." })); return; }

  const rows = board.programs;
  const cov = board.meta.coverage;
  const unwatched = rows.filter((r) => !r.watched);
  const failing = rows.filter((r) => ["stale", "broken", "blocked"].includes(r.health));
  const imprecise = rows.filter((r) => ["season", "unknown"].includes(r.precision));
  const unverified = rows.filter((r) => r.grad_2029 === "unverified");
  const ineligible = rows.filter((r) => r.grad_2029 === "ineligible");

  const wrap = el("div");
  wrap.append(el("p", { class: "note", style: "margin:18px 0" },
    "What this tracker can and cannot see. Everything here is a to-do list, not a status badge — ",
    el("b", { text: "a programme with no live checker is a prediction, not a fact." })));

  const stat = (label, n, sub) => el("div", { class: "tile" },
    el("div", { class: "tile-n", text: String(n) }),
    el("div", { class: "tile-k", text: label }),
    el("div", { class: "tile-sub", text: sub }));

  wrap.append(el("div", { class: "tiles" },
    stat("LIVE API", cov.auto, "structured job-board checks"),
    stat("MIRRORED", cov.mirror + cov.page_hash, "community lists / page diff"),
    stat("CURATED ONLY", cov.curated, "no automated check yet"),
    stat("FAILING", failing.length, "checkers needing attention"),
    stat("VAGUE DATES", imprecise.length, "month unknown"),
    stat("CLASS YEAR UNREAD", unverified.length, "eligibility not verified")));

  const table = (title, list, cells, headers) => {
    if (!list.length) return null;
    const t = el("table", { class: "t" },
      el("thead", {}, el("tr", {}, headers.map((h) => el("th", { text: h })))),
      el("tbody", {}, list.map((r) => el("tr", {}, cells(r).map((c) =>
        el("td", {}, c))))));
    return el("section", {}, el("h2", { class: "sect-h", text: `${title} · ${list.length}` }), t);
  };

  // `table()` returns null for an empty list; Node.append(null) would render the string
  // "null", so every section is filtered before it reaches the DOM.
  const sections = [
    table("Checkers failing", failing,
      (r) => [r.firm, r.health, r.last_error || "—", ago(r.last_ok)],
      ["Firm", "Health", "Last error", "Last good check"]),
    table("Not watched — curated prediction only", unwatched,
      (r) => [r.firm, r.program, r.window_label,
              el("a", { href: r.link, target: "_blank", rel: "noopener noreferrer", text: "site" })],
      ["Firm", "Programme", "Predicted window", "Link"]),
    table("Class-year requirement not yet verified", unverified,
      (r) => [r.firm, r.program, r.window_label,
              el("span", { title: r.soph_score_basis || "", text: `${r.soph_score ?? "—"}/100` }),
              el("a", { href: r.link, target: "_blank", rel: "noopener noreferrer", text: "check" })],
      ["Firm", "Programme", "Window", "Soph confidence", "Read the posting"]),
    table("Confirmed NOT open to the class of 2029", ineligible,
      (r) => [r.firm, r.program, r.grad_2029_basis || "—"],
      ["Firm", "Programme", "Why"]),
    table("Dates needing curation", imprecise,
      (r) => [r.firm, r.season_raw, r.window_label],
      ["Firm", "Curated season string", "Rendered as"]),
  ].filter(Boolean);
  for (const s of sections) wrap.append(s);

  mount.append(wrap);
}
