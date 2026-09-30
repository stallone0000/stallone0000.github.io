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
