(() => {
  const root = document.documentElement;
  const themeButton = document.querySelector('.theme-toggle');
  const systemTheme = window.matchMedia('(prefers-color-scheme: dark)');
  const isDark = () => root.dataset.theme ? root.dataset.theme === 'dark' : systemTheme.matches;
  const updateThemeLabel = () => {
    themeButton.textContent = isDark() ? 'Light' : 'Dark';
    themeButton.setAttribute('aria-label', `Switch to ${isDark() ? 'light' : 'dark'} mode`);
  };
  themeButton.hidden = false;
  updateThemeLabel();
  themeButton.addEventListener('click', () => {
    root.dataset.theme = isDark() ? 'light' : 'dark';
    try { localStorage.setItem('color-theme', root.dataset.theme); } catch (_) {}
    updateThemeLabel();
  });
  systemTheme.addEventListener('change', updateThemeLabel);
  const menu = document.querySelector('.menu-toggle');
  const nav = document.getElementById('navigation');
  const mobile = window.matchMedia('(max-width: 800px)');
  const closeMenu = () => {
    nav.classList.remove('is-open');
    menu.setAttribute('aria-expanded', 'false');
  };
  const syncMenu = () => { menu.hidden = !mobile.matches; closeMenu(); };
  menu.addEventListener('click', () => {
    const open = nav.classList.toggle('is-open');
    menu.setAttribute('aria-expanded', String(open));
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && nav.classList.contains('is-open')) {
      closeMenu(); menu.focus();
    }
  });
  mobile.addEventListener('change', syncMenu);
  syncMenu();
  root.classList.add('js');
  const printButton = document.querySelector('.print-button');
  if (printButton) {
    printButton.hidden = false;
    printButton.addEventListener('click', () => window.print());
  }
})();
