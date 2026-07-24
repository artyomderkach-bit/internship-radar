import { el, clear, ago } from "../render/fmt.js";
import { getBoard } from "../api.js";
import * as store from "../store.js";

const STAGE_CHIP = {
  interested: "notopen", applied: "open", OA: "soon", interview: "soon",
  offer: "open", rejected: "closed", passed: "closed",
};

function importFromFile(onDone) {
  const input = el("input", { type: "file", accept: "application/json",
                              style: "display:none" });
  input.addEventListener("change", async () => {
    const file = input.files?.[0];
    if (!file) return;
    try {
      const n = store.importObject(JSON.parse(await file.text()));
      alert(`Imported ${n} updated ${n === 1 ? "entry" : "entries"}.`);
      onDone();
    } catch (e) {
      alert(`Import failed: ${e.message}`);
    }
  });
  document.body.append(input);
  input.click();
  input.remove();
}

export async function render(mount, params) {
  clear(mount);

  // A sync link from another device: #/mine?d=<base64url>. Fragments never reach the server,
  // so the payload travels through iMessage/AirDrop without touching GitHub.
  const payload = params?.get("d");
  if (payload) {
    try {
      const n = store.importObject(store.decodeSync(payload));
      history.replaceState(null, "", "#/mine");
      alert(`Synced ${n} updated ${n === 1 ? "entry" : "entries"} from that link.`);
    } catch {
      alert("That sync link could not be read.");
    }
  }

  const { board } = await getBoard();
  const wrap = el("div");
  mount.append(wrap);

  const draw = () => {
    clear(wrap);
    const mine = store.all();
    const ids = Object.keys(mine);
    const byId = new Map((board?.programs || []).map((p) => [p.id, p]));
    const c = store.counts();

    wrap.append(el("p", { class: "note", style: "margin:18px 0" },
      el("b", { text: "Private to this browser." }),
      " Nothing on this page is in the repository or visible to anyone you send the link to. ",
      "Clearing site data wipes it — that's what export is for."));

    wrap.append(el("div", { class: "tiles" },
      el("div", { class: "tile" }, el("div", { class: "tile-n", text: String(c.applied) }),
        el("div", { class: "tile-k", text: "APPLIED" })),
      el("div", { class: "tile" }, el("div", { class: "tile-n", text: String(c.starred) }),
        el("div", { class: "tile-k", text: "STARRED" })),
      el("div", { class: "tile" }, el("div", { class: "tile-n", text: String(ids.length) }),
        el("div", { class: "tile-k", text: "TRACKED" }))));

    wrap.append(el("div", { class: "filters" },
      el("button", { class: "btn ghost", text: "Export JSON", onclick: () => {
        const a = el("a", { href: URL.createObjectURL(store.exportBlob()),
                            download: `radar-mine-${new Date().toISOString().slice(0, 10)}.json` });
        a.click(); URL.revokeObjectURL(a.href);
      } }),
      el("button", { class: "btn ghost", text: "Import JSON", onclick: () => importFromFile(draw) }),
      el("button", { class: "btn ghost", text: "Copy sync link", title:
        "A link containing your queue in the URL fragment — safe to send to your own phone.",
        onclick: async () => {
          try { await navigator.clipboard.writeText(store.syncLink()); alert("Sync link copied."); }
          catch { prompt("Copy this sync link:", store.syncLink()); }
        } }),
      el("button", { class: "btn ghost", text: store.personalHidden() ? "Show personal layer" : "Hide personal layer",
        onclick: () => { store.togglePersonalHidden(); location.reload(); } })));

    if (!ids.length) {
      wrap.append(el("div", { class: "panel" }, el("p", { class: "empty", style: "margin:0" },
        "Nothing tracked yet. On the board, hit ", el("b", { text: "+" }),
        " on any row to mark it applied — one click, timestamped automatically. ",
        "Applied rows fade out and drop off the hero rail, so logging an application makes the board quieter.")));
      return;
    }

    const rows = ids.map((id) => ({ id, entry: mine[id], prog: byId.get(id) }))
      .sort((a, b) => (b.entry.updated_at || "").localeCompare(a.entry.updated_at || ""));

    const tbody = el("tbody");
    for (const { id, entry, prog } of rows) {
      const select = el("select", { class: "fsearch", style: "min-width:120px",
        onchange: (e) => { store.set(id, { stage: e.target.value }); draw(); } });
      for (const s of store.STAGES) {
        select.append(el("option", { value: s, selected: entry.stage === s || null, text: s }));
      }
      const note = el("input", { class: "fsearch", value: entry.note || "", placeholder: "note…" });
      note.addEventListener("change", () => store.set(id, { note: note.value }));

      tbody.append(el("tr", {},
        el("td", {}, el("b", { text: prog ? prog.firm : id }),
          prog && el("div", { class: "note", text: prog.program })),
        el("td", {}, el("span", { class: `chip ${STAGE_CHIP[entry.stage] || "ghost"}`, text: entry.stage || "—" })),
        el("td", {}, select),
        el("td", { class: "num" }, entry.applied_at ? ago(entry.applied_at) : "—"),
        el("td", {}, note),
        el("td", {}, el("button", { class: "btn ghost", text: "✕", title: "Remove",
          onclick: () => { store.clearOne(id); draw(); } }))));
    }

    wrap.append(el("table", { class: "t" },
      el("thead", {}, el("tr", {}, ["Programme", "Stage", "Change", "Applied", "Note", ""]
        .map((h) => el("th", { text: h })))),
      tbody));
  };

  draw();
  window.addEventListener("radar:mine", draw);
  return () => window.removeEventListener("radar:mine", draw);
}
