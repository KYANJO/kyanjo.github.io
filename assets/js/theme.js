/* Apply a saved preference before the first paint. */
try {
  const savedTheme = localStorage.getItem('color-theme');
  if (savedTheme === 'light' || savedTheme === 'dark') {
    document.documentElement.dataset.theme = savedTheme;
  }
} catch (_) { /* System preference remains available when storage is blocked. */ }
