import { route, routeList, start, parseHash } from "./router.js";
import { el, clear, ago } from "./render/fmt.js";
import { getJSON } from "./api.js";
import { every } from "./poll.js";

import * as board from "./pages/board.js";
import * as timeline from "./pages/timeline.js";
import * as feed from "./pages/feed.js";
import * as mine from "./pages/mine.js";
import * as health from "./pages/health.js";

route("/board", board.render, "Board");
route("/timeline", timeline.render, "Timeline");
route("/feed", feed.render, "Feed");
route("/mine", mine.render, "Mine");
route("/health", health.render, "Health");

const nav = document.getElementById("nav");
const main = document.getElementById("main");
const banner = document.getElementById("banner");
const freshText = document.getElementById("freshness-text");
const freshBox = document.getElementById("freshness");
const brandSub = document.getElementById("brand-sub");

function drawNav(active) {
  clear(nav);
  for (const { path, label } of routeList()) {
    nav.append(el("a", { href: `#${path}`, class: path === active ? "on" : "", text: label }));
  }
}

// Cron jitter on GitHub Actions runs 5-20 minutes, so the header never promises a cadence.
// It reports the OBSERVED age of the data and escalates on its own. A frozen pipeline still
// tells the truth here because the age is computed client-side against the browser clock.
const LAG_MINUTES = 75;
const DEAD_HOURS = 3;

async function refreshFreshness() {
  const meta = await getJSON("meta.json");
  if (!meta) {
    freshBox.className = "freshness dead";
    freshText.textContent = "cannot reach data";
    return;
  }
  const stamp = meta.last_ok || meta.generated_at;
  const ageMin = (Date.now() - Date.parse(stamp)) / 60000;
  const watched = (meta.coverage?.auto || 0) + (meta.coverage?.mirror || 0);

  freshBox.className = "freshness";
  freshText.textContent = `built ${ago(meta.generated_at)}`;

  clear(banner);
  banner.hidden = true;

  if (watched === 0) {
    // Phase 0 reality: honest about being a curated board, not a live one.
    brandSub.textContent = "curated windows · live checks not yet enabled";
    freshBox.className = "freshness lagging";
  } else {
    brandSub.textContent = `${watched} programmes watched live`;
    if (ageMin > DEAD_HOURS * 60) {
      freshBox.className = "freshness dead";
      banner.hidden = false;
      banner.className = "";
      banner.textContent =
        `⚠ No successful check in ${ago(stamp)}. The scheduled job may be disabled — ` +
        `verify anything time-sensitive on the firm's own site.`;
    } else if (ageMin > LAG_MINUTES) {
      freshBox.className = "freshness lagging";
      banner.hidden = false;
      banner.className = "warn";
      banner.textContent = `Data is ${ago(stamp)} — later than the usual 30-minute cadence.`;
    }
  }
}

drawNav(parseHash().path);
start(main, (path) => {
  drawNav(path);
  main.scrollIntoView({ block: "start" });
});

refreshFreshness();
every(60_000, refreshFreshness, { immediate: false });

// Keyboard: 1-5 jump between views, / focuses search. Matches the desk's shortcuts.
document.addEventListener("keydown", (e) => {
  if (e.metaKey || e.ctrlKey || e.altKey) return;
  const tag = document.activeElement?.tagName;
  if (tag === "INPUT" || tag === "SELECT" || tag === "TEXTAREA") {
    if (e.key === "Escape") document.activeElement.blur();
    return;
  }
  const paths = routeList().map((r) => r.path);
  const n = parseInt(e.key, 10);
  if (n >= 1 && n <= paths.length) { location.hash = paths[n - 1]; return; }
  if (e.key === "/") {
    const search = document.querySelector(".fsearch");
    if (search) { e.preventDefault(); search.focus(); }
  }
});
