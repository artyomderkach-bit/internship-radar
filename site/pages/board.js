import { el, clear, frag, plural } from "../render/fmt.js";
import { rowEl, heroCard } from "../render/card.js";
import { densityStrip, sectorsOf } from "../render/density.js";
import { getBoard } from "../api.js";
import { setParams } from "../router.js";
import * as store from "../store.js";
import { every } from "../poll.js";

const BUCKET_ORDER = ["open_now", "blind_spot", "this_month", "next_60", "later", "closed"];

// Collapsed by default: the long tail. He should land on what's actionable.
const DEFAULT_COLLAPSED = new Set(["later", "closed"]);
const collapsed = new Set(DEFAULT_COLLAPSED);

function readFilters(params) {
  return {
    sec: params.get("sec") || "",
    loc: params.get("loc") || "",
    q: (params.get("q") || "").toLowerCase(),
    min: parseFloat(params.get("min") || "0") || 0,
    // Diversity-restricted programmes are hidden by DEFAULT — he can't apply to them — but
    // the count is always shown so they're never silently disappeared.
    div: params.get("div") === "1",
    doubt: params.get("doubt") === "1",
    // He graduates May 2029 and does not write code. Both of these hide by DEFAULT —
    // a programme he cannot apply to is worse than noise, it is a wasted evening.
    inelig: params.get("inelig") === "1",
    code: params.get("code") === "1",
    quant: params.get("quant") === "1",
    unver: params.get("unver") === "1",
    watched: params.get("watched") === "1",
    bucket: params.get("b") || "",
  };
}

function matches(r, f) {
  if (f.sec && r.sector !== f.sec) return false;
  if (f.loc && r.loc_bucket !== f.loc) return false;
  if (f.min && r.overall < f.min) return false;
  if (!f.div && r.elig_track === "div_only") return false;
  if (f.doubt && r.soph_confidence === "doubtful") return false;
  if (!f.inelig && r.grad_2029 === "ineligible") return false;
  if (!f.code && r.coding === "required") return false;
  if (!f.quant && r.quant_role) return false;
  if (f.unver && r.grad_2029 !== "eligible") return false;
  if (f.watched && !r.watched) return false;
  if (f.bucket && r.bucket !== f.bucket) return false;
  if (f.q) {
    const hay = `${r.firm} ${r.program} ${r.sub} ${r.loc} ${r.notes}`.toLowerCase();
    if (!hay.includes(f.q)) return false;
  }
  return true;
}

function tiles(counts, f) {
  const spec = [
    ["open_now", "t-open", "OPEN NOW", counts.open_now, "apply today"],
    ["this_month", "t-soon", "OPENS ≤31 DAYS", counts.this_month, "get ready"],
    ["blind_spot", "t-blind", "⚠ BLIND SPOTS", counts.blind_spot, "verify by hand"],
    ["later", "t-later", "TRACKING", counts.next_60 + counts.later, "later this cycle"],
    ["closed", "t-closed", "CLOSED", counts.closed, "missed or ended"],
  ];
  return el("div", { class: "tiles" }, spec.map(([key, cls, label, n, sub]) =>
    el("button", {
      class: `tile ${cls}${f.bucket === key ? " on" : ""}`,
      onclick: () => {
        const p = new URLSearchParams(location.hash.split("?")[1] || "");
        if (f.bucket === key) p.delete("b"); else p.set("b", key);
        setParams(p);
      },
    }, el("div", { class: "tile-n", text: String(n) }),
       el("div", { class: "tile-k", text: label }),
       el("div", { class: "tile-sub", text: sub }))));
}

/** The hero rail. NEVER empty — that's the whole point in August, when nothing is open. */
function hero(rows) {
  const open = rows.filter((r) => r.status === "open");
  const blind = rows.filter((r) => r.bucket === "blind_spot");
  const upcoming = rows
    .filter((r) => !["open_now", "blind_spot", "closed"].includes(r.bucket) && r.days_until >= 0)
    .slice(0, 6);

  let title, sub, cards;
  if (open.length) {
    title = "ACT NOW";
    sub = `${plural(open.length, "programme")} accepting applications`;
    cards = [...open, ...blind].slice(0, 6);
  } else {
    title = "NEXT TO OPEN";
    sub = "nothing is live yet — these are the nearest predicted windows";
    cards = [...blind, ...upcoming].slice(0, 6);
  }
  if (!cards.length) return null;

  return el("section", { class: "hero" },
    el("div", { class: "hero-h" }, title, " — ", el("em", { text: sub })),
    el("div", { class: "hero-rail" }, cards.map(heroCard)));
}

function filterBar(f, shown, total, counts, sectors) {
  const p = () => new URLSearchParams(location.hash.split("?")[1] || "");
  const set = (k, v) => { const q = p(); v ? q.set(k, v) : q.delete(k); setParams(q); };
  const pill = (k, val, label) => el("button", {
    class: `fbtn${f[k] === val ? " on" : ""}`, text: label,
    onclick: () => set(k, f[k] === val ? "" : val),
  });
  const check = (k, label, title) => el("label", { class: "fcheck", title },
    el("input", { type: "checkbox", checked: f[k] || null,
                  onchange: (e) => set(k, e.target.checked ? "1" : "") }),
    label);

  const search = el("input", { class: "fsearch", type: "search", placeholder: "search firms…",
                               value: f.q });
  let t = null;
  search.addEventListener("input", (e) => {
    clearTimeout(t);
    const v = e.target.value;
    t = setTimeout(() => set("q", v), 160);
  });

  return el("div", { class: "filters" },
    // Sectors come from the data, not a hard-coded list — the sister board carries
    // "HR & Talent" instead of "Consulting" and this bar must tell the truth on both.
    el("div", { class: "fgroup" }, el("span", { text: "sector" }),
      sectors.map((s) => pill("sec", s, s))),
    el("div", { class: "fgroup" }, el("span", { text: "where" }),
      pill("loc", "Houston", "Houston"), pill("loc", "NYC", "NYC"), pill("loc", "Other", "Other")),
    check("div", `show diversity-only (${counts.div_only})`,
          "Affinity-restricted programmes. Hidden by default because they aren't open to you."),
    check("doubt", "hide doubtful sophomore fit",
          "Rows whose curated notes suggest they really target juniors / penultimate-year students."),
    check("watched", "auto-watched only",
          "Only programmes with a live checker. Everything else is a prediction from last cycle."),
    check("inelig", `show class-of-2029 ineligible (${counts.inelig})`,
          "Programmes that require graduating by 2028 — you graduate May 2029, so Summer 2027 "
          + "is your sophomore summer and these are recruiting a year ahead of you."),
    check("code", `show coding-required (${counts.code})`,
          "Postings that list Python/SQL/programming as a requirement."),
    check("quant", `show quant trading roles (${counts.quant})`,
          "Quant trading, market making and quant research seats. Hidden because they all "
          + "want programming — non-quant roles at the same firms still show."),
    check("unver", "only confirmed eligible",
          "Hide everything whose class-year requirement hasn't been read off the posting yet."),
    search,
    el("span", { class: "fcount" }, `${shown} of ${total}`,
      shown !== total ? el("button", { class: "fbtn", text: "clear", style: "margin-left:8px",
        onclick: () => setParams(new URLSearchParams()) }) : null));
}

function bucketSection(key, label, rows, rerender) {
  const isCollapsed = collapsed.has(key);
  const head = el("button", { class: "bucket-h",
    onclick: () => { isCollapsed ? collapsed.delete(key) : collapsed.add(key); rerender(); } },
    el("span", { class: "caret", text: isCollapsed ? "▸" : "▾" }),
    el("span", { text: label }),
    el("span", { class: "n", text: String(rows.length) }));

  const sec = el("section", { class: `bucket b-${key}` }, head);
  if (isCollapsed) return sec;

  if (!rows.length) {
    sec.append(el("div", { class: "bucket-empty",
      text: key === "open_now"
        ? "Nothing open yet. The first windows are expected in August."
        : "None." }));
    return sec;
  }

  // Sub-group the big buckets by month — 51 rows all starting "Sep 1" is a wall otherwise.
  let lastMonth = null;
  for (const r of rows) {
    if (rows.length > 8 && r.month_group !== lastMonth) {
      lastMonth = r.month_group;
      sec.append(el("div", { class: "monthsep", text: r.month_group }));
    }
    sec.append(rowEl(r, { onChange: rerender }));
  }
  return sec;
}

function sidePanels(board, all) {
  const cov = board.meta.coverage;
  const total = board.meta.counts.total;
  const bar = (cls, label, n) => el("div", { class: `cov-row ${cls}` },
    el("span", { style: "min-width:64px", text: label }),
    el("span", { class: "cov-bar" }, el("i", { style: `width:${Math.round((n / total) * 100)}%` })),
    el("span", { class: "cov-n", text: String(n) }));

  const c = store.counts();
  const imprecise = board.meta.counts.imprecise;

  return el("aside", { class: "side" },
    el("div", { class: "panel" }, el("h3", { text: "Coverage" }),
      bar("auto", "live API", cov.auto),
      bar("mirror", "mirrored", cov.mirror + cov.page_hash),
      bar("curated", "curated", cov.curated),
      el("p", { class: "empty", style: "margin:9px 0 0",
        text: cov.auto + cov.mirror === 0
          ? "No live checkers yet — every window below is a prediction from last cycle. Automated checks land next."
          : `${cov.curated} programmes are still curated-only.` })),

    el("div", { class: "panel" }, el("h3", { text: "Date confidence" }),
      el("p", { class: "empty", style: "margin:0" },
        `${imprecise} of ${total} rows only say "Fall 2026" or similar — no month. `,
        "Those are shown with wide, faded windows and sort below rows with real dates.")),

    el("div", { class: "panel" }, el("h3", { text: "My queue · private" }),
      store.personalHidden()
        ? el("p", { class: "empty", style: "margin:0", text: "Personal layer hidden." })
        : el("p", { class: "empty", style: "margin:0" },
            `${c.applied} applied · ${c.starred} starred`, el("br"),
            "Stored only in this browser — never in the repo, never visible to anyone you send this link to."),
      el("div", { style: "margin-top:9px;display:flex;gap:6px;flex-wrap:wrap" },
        el("a", { class: "btn ghost", href: "#/mine", text: "Open" }),
        el("button", { class: "btn ghost", text: store.personalHidden() ? "Show" : "Hide",
          title: "Blank all personal state for screen-sharing",
          onclick: () => { store.togglePersonalHidden(); location.reload(); } }))));
}

export async function render(mount, params) {
  clear(mount);
  const wrap = el("div");
  mount.append(wrap);

  let board = null;

  const draw = () => {
    if (!board) return;
    clear(wrap);
    const f = readFilters(new URLSearchParams(location.hash.split("?")[1] || ""));
    const all = board.programs;
    const shown = all.filter((r) => matches(r, f));
    const counts = { ...board.meta.counts };
    for (const b of BUCKET_ORDER) counts[b] = shown.filter((r) => r.bucket === b).length;
    counts.div_only = all.filter((r) => r.elig_track === "div_only").length;
    counts.inelig = all.filter((r) => r.grad_2029 === "ineligible").length;
    counts.code = all.filter((r) => r.coding === "required").length;
    counts.quant = all.filter((r) => r.quant_role).length;
    counts.unverified = all.filter((r) => r.grad_2029 === "unverified").length;

    wrap.append(tiles(counts, f));
    const h = hero(shown.length ? shown : all);
    if (h) wrap.append(h);
    wrap.append(densityStrip(all, board.meta));

    const split = el("div", { class: "split" });
    const left = el("div");
    left.append(filterBar(f, shown.length, all.length, counts, sectorsOf(all)));
    for (const key of BUCKET_ORDER) {
      const rows = shown.filter((r) => r.bucket === key);
      if (!rows.length && ["closed", "blind_spot"].includes(key)) continue;
      left.append(bucketSection(key, board.meta.bucket_labels[key], rows, draw));
    }
    split.append(left, sidePanels(board, all));
    wrap.append(split);
  };

  const load = async () => {
    const { board: b } = await getBoard();
    if (!b) { clear(wrap); wrap.append(el("div", { class: "page-loading", text: "Could not load data." })); return; }
    board = b;
    draw();
  };

  await load();
  window.addEventListener("radar:mine", draw);
  const handle = every(60_000, load, { immediate: false });
  return () => { handle.stop(); window.removeEventListener("radar:mine", draw); };
}
