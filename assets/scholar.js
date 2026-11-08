// Read our cached snapshot, rather than querying the badge service per visitor.
(() => {
  const group = document.getElementById('scholar-metrics');
  const checked = document.getElementById('scholar-checked');
  if (!group || !checked) return;
  const scholarId = group.dataset.scholarId;
  const keys = ['citations', 'h_index', 'i10_index'];
  const storageKey = `scholar-stats:${scholarId}`;
  const format = new Intl.NumberFormat('en-US');
  const dateFormat = new Intl.DateTimeFormat('en-CA', {
    timeZone: 'Asia/Shanghai', year: 'numeric', month: '2-digit', day: '2-digit'
  });
  let currentTime = Date.parse(group.dataset.fetchedAt);
  let lastRequest = 0;
  let pending = false;

  function valid(data) {
    if (!data || data.schema_version !== 1 || data.scholar_id !== scholarId ||
        data.source !== 'https://github.com/dexhunter/google-scholar-badge') return false;
    if (!Number.isFinite(Date.parse(data.fetched_at))) return false;
    const m = data.metrics;
    return m && keys.every(key => Number.isSafeInteger(m[key]) && m[key] >= 0) &&
      m.h_index ** 2 <= m.citations && m.i10_index * 10 <= m.citations;
  }

  function show(data) {
    if (!valid(data) || Date.parse(data.fetched_at) < currentTime) return false;
    keys.forEach(key => {
      group.querySelector(`[data-metric="${key}"]`).textContent = format.format(data.metrics[key]);
    });
    const parts = Object.fromEntries(dateFormat.formatToParts(new Date(data.fetched_at))
      .filter(part => ['year', 'month', 'day'].includes(part.type)).map(part => [part.type, part.value]));
    checked.textContent = `Checked ${parts.year}-${parts.month}-${parts.day}`;
    checked.dateTime = data.fetched_at;
    checked.title = `Last checked: ${data.fetched_at}`;
    currentTime = Date.parse(data.fetched_at);
    group.dataset.fetchedAt = data.fetched_at;
    return true;
  }

  try {
    show(JSON.parse(localStorage.getItem(storageKey)));
  } catch {
    // The HTML snapshot remains available when browser storage is unavailable.
  }

  async function refresh() {
    if (pending || document.hidden || Date.now() - lastRequest < 3600000) return;
    pending = true;
    lastRequest = Date.now();
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 10000);
    try {
      const response = await fetch(group.dataset.snapshotUrl, {
        cache: 'no-store', credentials: 'omit', signal: controller.signal
      });
      if (!response.ok) throw new Error('Scholar snapshot unavailable');
      const data = await response.json();
      if (!show(data)) return;
      try { localStorage.setItem(storageKey, JSON.stringify(data)); } catch {}
    } catch {
      // Keep the last successful snapshot and its original check date.
    } finally {
      clearTimeout(timeout);
      pending = false;
    }
  }

  refresh();
  setInterval(refresh, 3600000);
  document.addEventListener('visibilitychange', () => {
    if (!document.hidden) refresh();
  });
})();
