// Read cumulative visitors without sending an additional tracking hit.
(() => {
  const count = document.getElementById('visitor-total');
  if (!count || !/^[a-z0-9]{12}$/.test(count.dataset.site)) return;
  const endpoint = new URL('https://revolvermaps2.com/api/feed.php');
  endpoint.searchParams.set('k', count.dataset.site);
  const format = new Intl.NumberFormat('en-US');
  let pending = false;

  async function refresh() {
    if (pending || document.hidden) return;
    pending = true;
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 10000);
    try {
      const response = await fetch(endpoint, {
        cache: 'no-store', credentials: 'omit', signal: controller.signal
      });
      if (!response.ok) throw new Error('Visitor statistics unavailable');
      const data = await response.json();
      if (data.error || !Number.isSafeInteger(data.total) || data.total < 0) {
        throw new Error('Invalid visitor count');
      }
      const value = format.format(data.total);
      if (count.textContent !== value) count.textContent = value;
    } catch {
      // Keep the last real count, or the initial dash when nothing has loaded.
    } finally {
      clearTimeout(timeout);
      pending = false;
    }
  }

  refresh();
  setInterval(refresh, 30000);
  document.addEventListener('visibilitychange', () => {
    if (!document.hidden) refresh();
  });
})();
