import { el, clear, ago } from "../render/fmt.js";
import { getEvents } from "../api.js";

const KIND_LABEL = {
  opened: "→ OPEN", closed: "→ closed", watch_broke: "⚠ watch broke",
  watch_recovered: "✓ watch recovered", blocked: "⚠ blocked",
  window_moved: "↗ window moved", added: "+ added", url_changed: "↻ url changed",
};

export async function render(mount) {
  clear(mount);
  const events = (await getEvents()) || [];
  const wrap = el("div");
  wrap.append(el("p", { class: "note", style: "margin:18px 0" },
    "Every status change, newest first — including infrastructure events. ",
    "A checker breaking is news too, so it appears in the same feed rather than hidden on a status page."));

  if (!events.length) {
    wrap.append(el("div", { class: "panel" },
      el("p", { class: "empty", style: "margin:0" },
        "No changes recorded yet. The event log starts filling once automated checks are live — ",
        "until then every window on the board is a prediction from last cycle.")));
  } else {
    for (const e of events) {
      wrap.append(el("div", { class: "row" },
        el("div", { class: "row-when" }, el("b", { text: ago(e.ts) })),
        el("div", { class: "row-main" },
          el("div", { class: "row-firm", text: e.id }),
          el("div", { class: "row-meta" },
            el("span", { class: "chip ghost", text: KIND_LABEL[e.kind] || e.kind }),
            e.note && el("span", { text: e.note })))));
    }
  }
  mount.append(wrap);
}
