// Polling registry, ported from the kalshi desk. Pauses when the tab is hidden and refreshes
// immediately on return — a tracker that keeps hammering a background tab is just rude, and
// the first thing he wants on refocus is fresh data, not a wait for the next tick.

const timers = new Set();

export function every(ms, fn, { immediate = true } = {}) {
  let id = null;
  const tick = async () => { try { await fn(); } catch (e) { console.warn("[poll]", e); } };
  const startTimer = () => { if (id == null) id = setInterval(tick, ms); };
  const stopTimer = () => { if (id != null) { clearInterval(id); id = null; } };

  const onVis = () => {
    if (document.hidden) stopTimer();
    else { tick(); startTimer(); }
  };
  document.addEventListener("visibilitychange", onVis);
  if (immediate) tick();
  if (!document.hidden) startTimer();

  const handle = {
    stop() {
      stopTimer();
      document.removeEventListener("visibilitychange", onVis);
      timers.delete(handle);
    },
  };
  timers.add(handle);
  return handle;
}

export function stopAll() {
  for (const h of [...timers]) h.stop();
}
