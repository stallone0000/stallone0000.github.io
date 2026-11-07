// Use the page's usable width so visible scrollbars do not unbalance the globe.
(() => {
  if (!document.querySelector('.intro-layout.with-globe')) return;
  const root = document.documentElement;
  let lastWidth = 0;
  const syncViewportSpace = () => {
    const width = root.clientWidth;
    if (width === lastWidth) return;
    lastWidth = width;
    root.style.setProperty('--half-viewport', `${width / 2}px`);
  };
  syncViewportSpace();
  if (window.ResizeObserver) new ResizeObserver(syncViewportSpace).observe(root);
  else window.addEventListener('resize', syncViewportSpace);
})();

const header = document.querySelector('.navbar');
const toggle = document.querySelector('.navbar-toggle');
function closeNavigation() {
  header.classList.remove('navigation-open');
  toggle.setAttribute('aria-expanded', 'false');
}
toggle.addEventListener('click', () => {
  const open = header.classList.toggle('navigation-open');
  toggle.setAttribute('aria-expanded', String(open));
});
header.querySelectorAll('a').forEach(link => link.addEventListener('click', closeNavigation));
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && header.classList.contains('navigation-open')) {
    closeNavigation();
    toggle.focus();
  }
});
