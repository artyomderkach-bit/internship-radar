import { el, clear } from "../render/fmt.js";
import { ganttChart } from "../render/density.js";
import { getBoard } from "../api.js";

export async function render(mount) {
  clear(mount);
  const { board } = await getBoard();
  if (!board) { mount.append(el("div", { class: "page-loading", text: "Could not load data." })); return; }

  const wrap = el("div");
  wrap.append(el("p", { class: "note", style: "margin:18px 0 4px" },
    "Every tracked programme across the Aug 2026 → Mar 2027 cycle. ",
    el("b", { text: "Bar opacity is date confidence" }),
    ": solid means the month is known, faded means the curation only said “Fall 2026”. ",
    el("b", { text: "Hatching means predicted" }), " — not yet observed live. Red line is today."));

  for (const sector of ["Energy", "Finance", "Consulting"]) {
    const rows = board.programs.filter((r) => r.sector === sector);
    if (!rows.length) continue;
    wrap.append(el("h2", { class: "sect-h", text: `${sector} · ${rows.length}` }));
    wrap.append(el("div", { class: "density" }, ganttChart(rows)));
  }
  mount.append(wrap);
}
