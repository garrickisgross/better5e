// JS for accounts/settings page
(function () {
  const alerts = document.getElementById('diceThemeAlerts');
  const urlInput = document.getElementById('id_dice_external_theme_url');
  const btnTest = document.getElementById('diceThemeTestBtn');
  const form = document.querySelector('form');

  function addAlert(kind, text) {
    const klass = kind === 'success' ? 'alert-success' : (kind === 'warning' ? 'alert-warning' : 'alert-error');
    const el = document.createElement('div');
    el.className = `alert ${klass} shadow`;
    el.innerHTML = `<span>${text}</span>`;
    alerts.prepend(el);
    setTimeout(() => { el.remove(); }, 7000);
  }

  function getCsrf() {
    const m = document.cookie.match(/csrftoken=([^;]+)/);
    return m ? decodeURIComponent(m[1]) : '';
  }

  async function postJSON(url, body) {
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrf() },
      body: JSON.stringify(body)
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.error || `Request failed: ${res.status}`);
    return data;
  }

  function b64url(s) {
    try { return btoa(unescape(encodeURIComponent(s))).replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,''); } catch (_) { return ''; }
  }

  function progressAlert(title, max) {
    const wrap = document.createElement('div');
    wrap.className = 'alert alert-info shadow flex-col items-stretch';
    wrap.innerHTML = `<div class="flex w-full justify-between items-center"><span>${title}</span><span data-count>0/${max}</span></div>
                      <progress class="progress progress-primary mt-2" value="0" max="${max}"></progress>`;
    alerts.prepend(wrap);
    return {
      el: wrap,
      inc() { const prog = wrap.querySelector('progress'); const cnt = wrap.querySelector('[data-count]'); prog.value = Number(prog.value)+1; cnt.textContent = `${prog.value}/${prog.max}`; },
      done(success=true, text='') { wrap.classList.remove('alert-info'); wrap.classList.add(success? 'alert-success' : 'alert-error'); if (text) wrap.querySelector('span').textContent = text; setTimeout(()=>wrap.remove(), 7000); }
    };
  }

  // Test button: validate and preview
  if (btnTest) btnTest.addEventListener('click', async () => {
    const testUrl = btnTest.dataset.testUrl;
    const url = urlInput.value.trim();
    if (!url) { addAlert('error', 'Enter a URL to test.'); return; }
    btnTest.disabled = true; btnTest.classList.add('loading');
    try {
      const t = await postJSON(testUrl, { url });
      try { localStorage.setItem('diceThemeMeta:'+b64url(url), JSON.stringify({ themeColor: t.themeColor || null, materialType: t.materialType || null })); } catch(_){}
      window.dispatchEvent(new CustomEvent('dice:theme-preview', { detail: { url } }));
      addAlert('success', 'Previewing theme with a d20 roll…');
    } catch (e) {
      addAlert('error', e.message);
    } finally {
      btnTest.disabled = false; btnTest.classList.remove('loading');
    }
  });

  // Intercept Save to prefetch theme assets, then submit form normally
  if (form) form.addEventListener('submit', async (ev) => {
    const url = urlInput.value.trim();
    if (!url) return; // no theme URL -> normal submit persists preset/finish
    ev.preventDefault();
    let progress;
    try {
      const testUrl = btnTest?.dataset.testUrl;
      if (!testUrl) throw new Error('Missing test endpoint');
      const t = await postJSON(testUrl, { url });
      const assets = t.assets || ['theme.config.json'];
      const baseB64 = b64url(url);
      try { localStorage.setItem('diceThemeMeta:'+baseB64, JSON.stringify({ themeColor: t.themeColor || null, materialType: t.materialType || null })); } catch(_){}
      progress = progressAlert('Saving and caching theme…', assets.length);
      const origin = window.location.origin;
      for (const rel of assets) {
        const safeRel = String(rel).replace(/^\/+/, '');
        const proxied = `${origin}/dice-theme/${baseB64}/${safeRel}`;
        const res = await fetch(proxied, { cache: 'reload' });
        if (!res.ok) throw new Error(`Failed ${rel}: ${res.status}`);
        await res.blob();
        progress.inc();
      }
      progress.done(true, 'Theme cached. Applying…');
      // Update live page preview then submit form to persist
      window.dispatchEvent(new CustomEvent('dice:theme-updated', { detail: { url } }));
      form.submit();
    } catch (e) {
      if (progress) progress.done(false, e.message || 'Failed to save theme');
      addAlert('error', e.message || 'Failed to save theme');
    }
  });
})();

