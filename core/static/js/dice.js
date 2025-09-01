// Dice roller behavior moved from base template to static file
(function () {
  const toggle = document.getElementById('diceToggle');
  const panel = document.getElementById('dicePanel');
  const closeBtn = document.getElementById('diceClose');

  const history = document.getElementById('diceHistory');
  const historyEmpty = document.getElementById('diceHistoryEmpty');
  const rollBtn = document.getElementById('diceRollBtn');
  const resetBtn = document.getElementById('diceResetBtn');
  const modMinus = document.getElementById('diceModMinus');
  const modPlus = document.getElementById('diceModPlus');
  const modValue = document.getElementById('diceModValue');

  const DICE = [2, 4, 6, 8, 10, 12, 20, 100];

  function readPrefs() {
    const el = document.getElementById('dice-user-prefs');
    if (!el) return {};
    try { return JSON.parse(el.textContent || '{}'); } catch (_) { return {}; }
  }

  const userPrefs = readPrefs();
  const state = {
    counts: {},
    mod: 0,
    preset: userPrefs.preset || 'amethyst',
    finish: userPrefs.finish || 'glossy',
    externalThemeUrl: userPrefs.externalThemeUrl || ''
  };
  DICE.forEach(s => state.counts[s] = 0);

  function hidePanel() { panel?.classList.add('hidden'); }
  function togglePanel() { panel?.classList.toggle('hidden'); }

  function updateRollCta() {
    const anyDice = DICE.some(s => state.counts[s] > 0);
    if (rollBtn) rollBtn.disabled = !anyDice && state.mod === 0;
  }

  function setBadge(sides) {
    const btn = panel?.querySelector(`button[data-sides="${sides}"]`);
    if (!btn) return;
    const badge = btn.querySelector('[data-badge]');
    const c = state.counts[sides] || 0;
    if (c > 0) {
      badge.textContent = String(c);
      badge.classList.remove('hidden');
      btn.classList.add('btn-secondary');
    } else {
      badge.classList.add('hidden');
      btn.classList.remove('btn-secondary');
    }
    updateRollCta();
  }

  function adjustDie(sides, delta) {
    const next = Math.max(0, (state.counts[sides] || 0) + delta);
    state.counts[sides] = next;
    setBadge(sides);
  }

  function updateMod(delta) {
    state.mod += delta;
    if (modValue) modValue.textContent = String(state.mod);
    updateRollCta();
  }

  function rollDie(sides) { return Math.floor(Math.random() * sides) + 1; }

  function renderRollEntry({ formula, total, breakdown, timestamp }) {
    if (!history || !historyEmpty) return;
    const entry = document.createElement('div');
    entry.className = 'rounded-lg p-2 hover:bg-base-300/40';

    const d20s = breakdown.find(b => b.sides === 20)?.values || [];
    const isCrit = d20s.some(v => v === 20);
    const isFail = !isCrit && d20s.some(v => v === 1);
    const totalCls = isCrit ? 'text-success' : (isFail ? 'text-error' : '');

    const chips = breakdown.flatMap(b => b.values.map(v => `<span class=\"badge badge-ghost badge-sm rounded-full\">${v}</span>`)).join(' ');

    entry.innerHTML = `
      <div class="flex items-start justify-between gap-3">
        <div class="text-sm">
          <div class="opacity-70">${formula}</div>
          <div class="mt-1 flex flex-wrap gap-1">${chips || ''}</div>
        </div>
        <div class="text-right">
          <div class="text-2xl font-bold ${totalCls}">${total}</div>
          <div class="text-xs opacity-60">${timestamp}</div>
        </div>
      </div>`;

    entry.classList.add('opacity-0', 'translate-y-2');
    const nearBottom = (history.scrollHeight - history.clientHeight - history.scrollTop) < 8;
    history.appendChild(entry);
    historyEmpty.classList.add('hidden');
    if (nearBottom) history.scrollTop = history.scrollHeight;
    requestAnimationFrame(() => {
      entry.classList.add('transition-all', 'duration-300');
      entry.classList.remove('opacity-0');
      entry.classList.remove('translate-y-2');
    });
  }

  const PRESETS = {
    amethyst: { color: '#8b5cf6' },
    emerald: { color: '#10b981' },
    ruby: { color: '#ef4444' },
    sapphire: { color: '#60a5fa' },
    obsidian: { color: '#111827' },
    ivory: { color: '#e5e7eb' },
    gold: { color: '#f59e0b' },
    pumpkin: { color: '#fb923c' }
  };
  const FINISH = {
    matte: { lightIntensity: 0.75, shadows: true },
    glossy: { lightIntensity: 1.1, shadows: true },
    pearl: { lightIntensity: 0.95, shadows: true }
  };

  const dice3d = { box: null, ready: false };
  function b64url(s) {
    try { return btoa(unescape(encodeURIComponent(s))).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, ''); } catch (_) { return ''; }
  }
  function proxiedThemeBase(url) {
    if (!url) return '';
    const b64 = b64url(url);
    const origin = window.location.origin;
    return `${origin}/dice-theme/${b64}`;
  }
  function themeMetaFromStorage(url) {
    try { const v = localStorage.getItem('diceThemeMeta:' + b64url(url)); return v ? JSON.parse(v) : null; } catch (_) { return null; }
  }
  function currentThemeColor(urlOverride) {
    const url = urlOverride || state.externalThemeUrl;
    if (url) {
      const meta = themeMetaFromStorage(url);
      if (meta && meta.themeColor) return meta.themeColor;
    }
    return (PRESETS[state.preset] || PRESETS.amethyst).color;
  }

  async function ensureDice3D() {
    if (dice3d.ready && dice3d.box) return dice3d.box;
    const mod = await import('https://unpkg.com/@3d-dice/dice-box@1.1.4/dist/dice-box.es.min.js');
    const DiceBox = mod.default;
    const finish = FINISH[state.finish] || FINISH.glossy;
    const hasTheme = !!state.externalThemeUrl;
    const opts = {
      container: '#diceStage',
      id: 'dice-canvas',
      origin: 'https://unpkg.com',
      assetPath: '/@3d-dice/dice-box@1.1.4/dist/assets/',
      theme: hasTheme ? 'user-external' : 'default',
      delay: 12,
      scale: 5
    };
    if (hasTheme) {
      opts.externalThemes = { 'user-external': proxiedThemeBase(state.externalThemeUrl) };
      const color = currentThemeColor(); if (color) opts.themeColor = color;
    } else {
      const preset = PRESETS[state.preset] || PRESETS.amethyst;
      opts.themeColor = preset.color;
      opts.enableShadows = finish.shadows;
      opts.lightIntensity = finish.lightIntensity;
    }
    dice3d.box = new DiceBox(opts);
    await dice3d.box.init();
    dice3d.box.onRollComplete = function () {
      try { setTimeout(() => dice3d.box.hide(), 400); } catch (_) { }
    };
    dice3d.ready = true;
    return dice3d.box;
  }

  async function doRoll() {
    const notations = [];
    const parts = [];
    DICE.forEach(s => {
      const count = state.counts[s];
      if (!count) return;
      notations.push({ sides: `d${s}`, qty: count });
      parts.push(`${count}d${s}`);
    });
    if (notations.length === 0 && state.mod === 0) return;
    let formula = parts.join(' + ');
    if (state.mod) {
      const sign = state.mod > 0 ? '+' : '−';
      const modAbs = Math.abs(state.mod);
      formula = formula ? `${formula} ${sign} ${modAbs}` : `${sign} ${modAbs}`;
    }

    const box = await ensureDice3D();
    const hasTheme = !!state.externalThemeUrl;
    const updateOpts = { theme: hasTheme ? 'user-external' : 'default' };
    if (hasTheme) {
      updateOpts.externalThemes = { 'user-external': proxiedThemeBase(state.externalThemeUrl) };
      const color = currentThemeColor(); if (color) updateOpts.themeColor = color;
    } else {
      const preset = PRESETS[state.preset] || PRESETS.amethyst;
      const finish = FINISH[state.finish] || FINISH.glossy;
      updateOpts.themeColor = preset.color;
      updateOpts.enableShadows = finish.shadows;
      updateOpts.lightIntensity = finish.lightIntensity;
    }
    await box.updateConfig(updateOpts);
    box.show();

    let resultsArray = [];
    try {
      const rollOpts = hasTheme ? { theme: 'user-external', externalThemes: { 'user-external': proxiedThemeBase(state.externalThemeUrl) }, themeColor: currentThemeColor() } : { theme: 'default', themeColor: (PRESETS[state.preset] || PRESETS.amethyst).color };
      if (!hasTheme) { const f = FINISH[state.finish] || FINISH.glossy; rollOpts.enableShadows = f.shadows; rollOpts.lightIntensity = f.lightIntensity; }
      resultsArray = await box.roll(notations, rollOpts);
    } catch (e) {
      resultsArray = [];
      DICE.forEach(s => {
        const count = state.counts[s];
        for (let i = 0; i < count; i++) resultsArray.push({ sides: s, value: rollDie(s) });
      });
    }

    const bySides = new Map();
    for (const r of resultsArray) {
      const s = typeof r.sides === 'string' ? parseInt(String(r.sides).replace(/\D/g, '')) : r.sides;
      if (!bySides.has(s)) bySides.set(s, []);
      if (Number.isFinite(r.value)) bySides.get(s).push(r.value);
    }
    const breakdown = Array.from(bySides.entries()).map(([sides, values]) => ({ sides, values }));
    let total = 0;
    for (const values of bySides.values()) total += values.reduce((a, b) => a + b, 0);
    total += state.mod;
    const timestamp = new Date().toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
    renderRollEntry({ formula, total, breakdown, timestamp });
  }

  document.addEventListener('click', (e) => {
    const within = e.target.closest('#diceFab');
    if (!within) hidePanel();
  });
  if (toggle) toggle.addEventListener('click', (e) => { e.stopPropagation(); togglePanel(); });
  if (closeBtn) closeBtn.addEventListener('click', (e) => { e.stopPropagation(); hidePanel(); });

  if (panel) {
    panel.addEventListener('click', (e) => {
      const btn = e.target.closest('button[data-sides]');
      if (!btn) return;
      const sides = parseInt(btn.getAttribute('data-sides'), 10);
      if (!Number.isFinite(sides)) return;
      const delta = (e.shiftKey || e.altKey || e.metaKey) ? -1 : 1;
      adjustDie(sides, delta);
    });
    panel.addEventListener('contextmenu', (e) => {
      const btn = e.target.closest('button[data-sides]');
      if (!btn) return;
      e.preventDefault();
      const sides = parseInt(btn.getAttribute('data-sides'), 10);
      adjustDie(sides, -1);
    });
  }

  if (modMinus) modMinus.addEventListener('click', (e) => updateMod(e.shiftKey ? -5 : -1));
  if (modPlus) modPlus.addEventListener('click', (e) => updateMod(e.shiftKey ? 5 : 1));
  if (resetBtn) resetBtn.addEventListener('click', () => {
    DICE.forEach(s => { state.counts[s] = 0; setBadge(s); });
    state.mod = 0; if (modValue) modValue.textContent = '0';
    updateRollCta();
  });
  if (rollBtn) rollBtn.addEventListener('click', () => doRoll());

  updateRollCta();

  window.addEventListener('dice:theme-updated', async (e) => {
    try {
      const url = e.detail && e.detail.url ? String(e.detail.url) : '';
      state.externalThemeUrl = url;
      const box = await ensureDice3D();
      const hasTheme = !!state.externalThemeUrl;
      const opts = { theme: hasTheme ? 'user-external' : 'default' };
      if (hasTheme) {
        opts.externalThemes = { 'user-external': proxiedThemeBase(state.externalThemeUrl) };
        const color = currentThemeColor(); if (color) opts.themeColor = color;
      } else {
        const preset = PRESETS[state.preset] || PRESETS.amethyst;
        const finish = FINISH[state.finish] || FINISH.glossy;
        opts.themeColor = preset.color; opts.enableShadows = finish.shadows; opts.lightIntensity = finish.lightIntensity;
      }
      await box.updateConfig(opts);
    } catch (err) { console.warn('Failed to apply theme update', err); }
  });

  window.addEventListener('dice:theme-preview', async (e) => {
    const newUrl = e.detail && e.detail.url ? String(e.detail.url) : '';
    if (!newUrl) return;
    const prevUrl = state.externalThemeUrl;
    try {
      const box = await ensureDice3D();
      const ext = { 'user-external': proxiedThemeBase(newUrl) };
      const color = currentThemeColor(newUrl);
      await box.updateConfig({ theme: 'user-external', externalThemes: ext, themeColor: color });
      await box.roll([{ sides: 'd20', qty: 1 }], { theme: 'user-external', externalThemes: ext, themeColor: color });
    } catch (err) {
      console.warn('Preview failed', err);
    } finally {
      try {
        const box = await ensureDice3D();
        state.externalThemeUrl = prevUrl;
        const hasTheme = !!state.externalThemeUrl;
        const opts = { theme: hasTheme ? 'user-external' : 'default' };
        if (hasTheme) {
          opts.externalThemes = { 'user-external': proxiedThemeBase(state.externalThemeUrl) };
          const color2 = currentThemeColor(); if (color2) opts.themeColor = color2;
        } else {
          const preset = PRESETS[state.preset] || PRESETS.amethyst;
          const finish = FINISH[state.finish] || FINISH.glossy;
          opts.themeColor = preset.color; opts.enableShadows = finish.shadows; opts.lightIntensity = finish.lightIntensity;
        }
        await box.updateConfig(opts);
      } catch (_) { }
    }
  });
})();

