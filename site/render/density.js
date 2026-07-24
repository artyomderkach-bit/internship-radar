// Season views, hand-rolled inline SVG.
//
// Deliberately NOT a charting library: this is ~100 lines of <rect> and <text>, and vendoring
// 1 MB of ECharts onto a repo whose selling point is "no build step" would be absurd.
//
// The one idea both views encode: opacity == precision. A bar for "Fall 2026 (Sep–Nov)" is
// solid because we actually know it; a bar for bare "Fall 2026" is faded and hatched because
// we're guessing the month. The chart is not allowed to look more certain than the data.

import { el } from "./fmt.js";

const SVG = "http://www.w3.org/2000/svg";
const CYCLE_START = new Date("2026-08-01T00:00:00Z");
const CYCLE_END = new Date("2027-03-31T00:00:00Z");
const SPAN = CYCLE_END - CYCLE_START;

const MONTHS = [
  ["Aug", "2026-08-01"], ["Sep", "2026-09-01"], ["Oct", "2026-10-01"], ["Nov", "2026-11-01"],
  ["Dec", "2026-12-01"], ["Jan", "2027-01-01"], ["Feb", "2027-02-01"], ["Mar", "2027-03-01"],
];

const OPACITY = { month_range: 0.95, month: 0.95, quarter: 0.6, season: 0.42, unknown: 0.22 };
const SECTOR_COLOR = { Energy: "#f59e0b", Finance: "#60a5fa", Consulting: "#22c55e" };

const svgEl = (tag, attrs = {}) => {
  const n = document.createElementNS(SVG, tag);
  for (const [k, v] of Object.entries(attrs)) if (v != null) n.setAttribute(k, String(v));
  return n;
};

const pct = (iso) => {
  const t = new Date(iso + (iso.length === 10 ? "T00:00:00Z" : ""));
  return Math.max(0, Math.min(100, ((t - CYCLE_START) / SPAN) * 100));
};

function hatchDefs(id) {
  const defs = svgEl("defs");
  const p = svgEl("pattern", { id, width: 6, height: 6, patternUnits: "userSpaceOnUse",
                               patternTransform: "rotate(45)" });
  p.append(svgEl("rect", { width: 6, height: 6, fill: "transparent" }));
  p.append(svgEl("rect", { width: 2, height: 6, fill: "rgba(255,255,255,.35)" }));
  defs.append(p);
  return defs;
}

function axis(svg, height) {
  for (const [label, iso] of MONTHS) {
    const x = pct(iso);
    svg.append(svgEl("line", { x1: `${x}%`, x2: `${x}%`, y1: 14, y2: height,
                               stroke: "rgba(255,255,255,.07)", "stroke-width": 1 }));
    const t = svgEl("text", { x: `${x}%`, y: 10, fill: "#93a3c0", "font-size": 10,
                              "font-family": "ui-monospace, monospace", dx: 3 });
    t.textContent = label;
    svg.append(t);
  }
  const today = pct(new Date().toISOString().slice(0, 10));
  svg.append(svgEl("line", { x1: `${today}%`, x2: `${today}%`, y1: 12, y2: height,
                             stroke: "#ef4444", "stroke-width": 1.5, "stroke-dasharray": "3 2" }));
}

/** How many programmes could open in each month, split by how sure we are of the date. */
function monthCounts(rows) {
  return MONTHS.map(([label, iso]) => {
    const monthStart = new Date(iso + "T00:00:00Z");
    const monthEnd = new Date(monthStart);
    monthEnd.setUTCMonth(monthEnd.getUTCMonth() + 1);
    let precise = 0, vague = 0;
    for (const r of rows) {
      const covers = r.windows.some((w) =>
        new Date(w.start + "T00:00:00Z") < monthEnd && new Date(w.end + "T00:00:00Z") >= monthStart);
      if (!covers) continue;
      const sure = r.windows.some((w) => (w.precision === "month" || w.precision === "month_range")
        && new Date(w.start + "T00:00:00Z") < monthEnd && new Date(w.end + "T00:00:00Z") >= monthStart);
      sure ? precise++ : vague++;
    }
    return { label, iso, precise, vague, total: precise + vague };
  });
}

/** Compact per-sector histogram for the board page: "when is the crush?" without a click.
 *
 * Drawn as bars-per-month rather than one rect per programme. Overlaying 27 overlapping
 * windows just produces one solid block that says nothing; a histogram actually shows that
 * September carries three times the load of any other month. */
export function densityStrip(rows, meta) {
  const sectors = ["Energy", "Finance", "Consulting"];
  const grid = el("div", { class: "dgrid" });
  const H = 34;
  const perSector = sectors.map((s) => monthCounts(rows.filter((r) => r.sector === s)));
  const max = Math.max(1, ...perSector.flat().map((m) => m.total));
  const slot = 100 / MONTHS.length;

  sectors.forEach((sector, si) => {
    const counts = perSector[si];
    const n = rows.filter((r) => r.sector === sector).length;
    const svg = svgEl("svg", { width: "100%", height: H, style: "display:block;overflow:visible" });

    counts.forEach((m, i) => {
      const x = i * slot + slot * 0.16;
      const w = slot * 0.68;
      const hTotal = (m.total / max) * (H - 4);
      const hPrecise = (m.precise / max) * (H - 4);
      if (m.total) {
        // Faded upper segment = "some month in this season, we don't know which".
        svg.append(svgEl("rect", { x: `${x}%`, y: H - hTotal, width: `${w}%`, height: hTotal,
                                   rx: 1.5, fill: SECTOR_COLOR[sector], opacity: 0.3 }));
        if (m.precise) {
          svg.append(svgEl("rect", { x: `${x}%`, y: H - hPrecise, width: `${w}%`, height: hPrecise,
                                     rx: 1.5, fill: SECTOR_COLOR[sector], opacity: 0.95 }));
        }
        const t = svgEl("text", { x: `${x + w / 2}%`, y: H - hTotal - 2.5, fill: "#93a3c0",
                                  "font-size": 9, "text-anchor": "middle",
                                  "font-family": "ui-monospace, monospace" });
        t.textContent = String(m.total);
        svg.append(t);
      }
    });

    const today = pct(new Date().toISOString().slice(0, 10));
    svg.append(svgEl("line", { x1: `${today}%`, x2: `${today}%`, y1: 0, y2: H,
                               stroke: "#ef4444", "stroke-width": 1.5 }));
    grid.append(el("div", { class: "dlabel" }, sector, " ", el("span", { text: `(${n})` })),
                el("div", {}, svg));
  });

  // Month ruler. Centred on each histogram slot, not on date-proportional positions.
  const ruler = svgEl("svg", { width: "100%", height: 14, style: "display:block;overflow:visible" });
  MONTHS.forEach(([label], i) => {
    const t = svgEl("text", { x: `${i * slot + slot / 2}%`, y: 10, fill: "#93a3c0",
                              "font-size": 10, "text-anchor": "middle",
                              "font-family": "ui-monospace, monospace" });
    t.textContent = label;
    ruler.append(t);
  });
  grid.append(el("div", {}), el("div", {}, ruler));

  return el("section", { class: "density" },
    el("h3", {}, "Season density — Aug 2026 → Mar 2027 · ",
      el("span", { style: "text-transform:none;letter-spacing:0",
        text: "solid = month known · faded = season only · red line = today" })),
    grid);
}

/** Full per-programme Gantt for #/timeline.
 *
 * Labels live in an HTML gutter rather than inside the SVG — drawing them at x=0 puts them
 * underneath the bars, which is unreadable once bars start in August. */
export function ganttChart(rows) {
  const ROW_H = 20;
  const grid = el("div", { class: "gantt" });

  // Header row: month ruler over the bar column only.
  const ruler = svgEl("svg", { width: "100%", height: 15, style: "display:block" });
  for (const [label, iso] of MONTHS) {
    const t = svgEl("text", { x: `${pct(iso)}%`, y: 11, fill: "#93a3c0", "font-size": 10,
                              "font-family": "ui-monospace, monospace", dx: 3 });
    t.textContent = label;
    ruler.append(t);
  }
  grid.append(el("div", {}), el("div", {}, ruler));

  const today = pct(new Date().toISOString().slice(0, 10));

  for (const r of rows) {
    const svg = svgEl("svg", { width: "100%", height: ROW_H, style: "display:block" });
    svg.append(hatchDefs(`h-${r.id}`));
    for (const [, iso] of MONTHS) {
      svg.append(svgEl("line", { x1: `${pct(iso)}%`, x2: `${pct(iso)}%`, y1: 0, y2: ROW_H,
                                 stroke: "rgba(255,255,255,.06)" }));
    }
    for (const w of r.windows) {
      const x = pct(w.start), width = Math.max(0.7, pct(w.end) - x);
      // Solid = we have actually observed this live. Hatched = still a prediction.
      const confirmed = r.status === "open" || r.first_seen_open;
      svg.append(svgEl("rect", {
        x: `${x}%`, y: 3, width: `${width}%`, height: ROW_H - 6, rx: 3,
        fill: SECTOR_COLOR[r.sector] || "#60a5fa", opacity: OPACITY[w.precision] ?? 0.3,
      }));
      if (!confirmed) {
        svg.append(svgEl("rect", {
          x: `${x}%`, y: 3, width: `${width}%`, height: ROW_H - 6, rx: 3,
          fill: `url(#h-${r.id})`, opacity: 0.2,
        }));
      }
      const tip = svgEl("title");
      tip.textContent = `${r.firm} — ${r.program}\n${r.window_label}\n${w.basis}`;
      svg.append(tip);
    }
    svg.append(svgEl("line", { x1: `${today}%`, x2: `${today}%`, y1: 0, y2: ROW_H,
                               stroke: "#ef4444", "stroke-width": 1.5 }));

    grid.append(
      el("div", { class: "glabel", title: `${r.firm} — ${r.program}` },
        el("b", { text: r.firm }), " ", el("span", { text: r.program })),
      el("div", {}, svg));
  }
  return grid;
}
