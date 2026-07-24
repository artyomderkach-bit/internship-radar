import { el, untilText } from "./fmt.js";
import * as store from "../store.js";

const BROKEN_HEALTH = new Set(["stale", "broken", "blocked"]);

/** Is this row one the tool is currently failing to watch, inside its live window? */
export const isBlind = (r) => r.bucket === "blind_spot";

export function statusChip(r) {
  if (r.status === "open") {
    if (r.confidence === "low") return el("span", { class: "chip likely", text: "likely — verify" });
    if (r.confidence === "medium") {
      // Curated-by-hand or mirrored from a community list: real, but not machine-verified
      // by us. Outlined rather than filled so it never reads as a live confirmed check.
      const via = r.check_method === "manual" ? "open · curated" : "open (mirror)";
      return el("span", { class: "chip likely", title: r.evidence || "", text: via });
    }
    return el("span", { class: "chip open", text: "open" });
  }
  if (isBlind(r)) return el("span", { class: "chip blind", text: "can't see" });
  if (r.status === "closed") return el("span", { class: "chip closed", text: "closed" });
  if (r.days_until >= 0 && r.days_until <= 14) return el("span", { class: "chip soon", text: "opens soon" });
  return el("span", { class: "chip notopen", text: "not open yet" });
}

/** How we know — or that we don't. Never let "curated guess" look like a live check. */
export function methodChip(r) {
  const label = {
    manual: "curated", github_mirror: "mirror", page_hash: "page-diff",
    greenhouse: "API", lever: "API", ashby: "API", smartrecruiters: "API", workday: "API",
  }[r.check_method] || r.check_method;
  const title = r.check_method === "manual"
    ? "Not watched automatically — this window is a prediction from last cycle."
    : `Watched via ${r.check_method}${r.last_ok ? "" : " (no successful check yet)"}`;
  return el("span", { class: "chip ghost", text: label, title });
}

export function rowEl(r, { onChange } = {}) {
  const mine = store.personalHidden() ? null : store.get(r.id);
  const done = !!mine && store.DONE_STAGES.has(mine.stage);

  const cls = ["row"];
  if (r.status === "open") cls.push("s-open");
  else if (r.status === "closed") cls.push("s-closed");
  else if (r.days_until >= 0 && r.days_until <= 14) cls.push("s-soon");
  if (BROKEN_HEALTH.has(r.health)) cls.push(`h-${r.health}`);
  if (isBlind(r)) cls.push("is-blind");
  if (done) cls.push("applied");

  const when = el("div", { class: "row-when" },
    el("b", { text: r.status === "open" ? "OPEN" : untilText(r.days_until, r.precision) }),
    r.window_label);

  const meta = el("div", { class: "row-meta" },
    statusChip(r),
    r.deadline && el("span", { class: "chip soon", title: "Application deadline",
                               text: `due ${r.deadline.slice(5)}` }),
    r.rolling && el("span", { class: "chip rolling", title: "Rolling — applications are reviewed as they arrive, so applying late costs you.", text: "rolling" }),
    r.soph_confidence === "doubtful" && el("span", { class: "chip doubt", title: "The curated notes suggest this may really target juniors/penultimate-year students.", text: "soph?" }),
    r.elig_track === "div_only" && el("span", { class: "chip ghost", text: "diversity-only" }),
    methodChip(r),
    el("span", { text: `${r.loc_bucket} · ${r.sub}` }));

  const applyUrl = r.apply_url || r.link;
  const act = el("div", { class: "row-act" },
    el("span", { class: "score", title: `selectivity ${r.sel} · prestige ${r.pres}`, text: r.overall.toFixed(1) }),
    el("a", { class: "btn", href: applyUrl, target: "_blank", rel: "noopener noreferrer",
              text: r.status === "open" ? "Apply" : "Site" }),
    !store.personalHidden() && el("button", {
      class: `btn ghost${done ? " on" : ""}`,
      title: done ? "Marked applied — click to undo" : "Mark applied (private to this browser)",
      text: done ? "✓" : "+",
      onclick: () => { store.toggleApplied(r.id); onChange?.(); },
    }));

  return el("div", { class: cls.join(" ") }, when,
    el("div", { class: "row-main" },
      el("div", { class: "row-firm" }, r.firm, " ", el("span", { class: "prog", text: r.program })),
      meta),
    act);
}

/** Hero card. Bigger, fewer, and the only place a red card is allowed. */
export function heroCard(r) {
  const cls = ["hcard"];
  if (r.status === "open") cls.push("is-open");
  else if (isBlind(r)) cls.push("is-blind");
  else if (r.days_until <= 14) cls.push("is-soon");

  const headline = r.status === "open" ? "OPEN NOW"
    : isBlind(r) ? "CAN'T SEE"
    : untilText(r.days_until, r.precision);

  return el("a", { class: cls.join(" "), href: r.apply_url || r.link,
                   target: "_blank", rel: "noopener noreferrer" },
    el("div", { class: "hcard-firm", text: r.firm }),
    el("div", { class: "hcard-prog", text: r.program }),
    el("div", { class: "hcard-when", text: headline }),
    el("div", { class: "hcard-meta" },
      el("span", { text: r.window_label }),
      r.deadline && el("span", { class: "chip soon", title: "Application deadline",
                               text: `due ${r.deadline.slice(5)}` }),
    r.rolling && el("span", { class: "chip rolling", text: "rolling" }),
      isBlind(r) && el("span", { class: "chip blind", text: r.last_error || "watch down" }),
      el("span", { class: "score", text: r.overall.toFixed(1) })));
}
