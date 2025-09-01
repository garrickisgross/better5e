// Theme toggle behavior and persistence
(function () {
  const toggleBtn = document.getElementById('themeToggleBtn');

  function setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    try { localStorage.setItem('theme', theme); } catch (_) {}
  }

  function currentTheme() {
    return document.documentElement.getAttribute('data-theme') || 'cupcake';
  }

  if (toggleBtn) {
    toggleBtn.addEventListener('click', function () {
      const next = currentTheme() === 'dark' ? 'cupcake' : 'dark';
      setTheme(next);
    });
  }
})();

