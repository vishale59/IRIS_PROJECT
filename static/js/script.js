/* ═══════════════════════════════════════════════════════════════════════════
   IRIS — Premium SaaS JavaScript
   Pure vanilla JS · No frameworks
   ═══════════════════════════════════════════════════════════════════════════ */

'use strict';

/* ─────────────────────────────────────────────────────────────
   SIDEBAR
   ───────────────────────────────────────────────────────────── */
const Sidebar = (() => {
  let sidebar, backdrop, hamburger;

  function open() {
    sidebar?.classList.add('open');
    backdrop?.classList.add('show');
    document.body.style.overflow = 'hidden';
  }
  function close() {
    sidebar?.classList.remove('open');
    backdrop?.classList.remove('show');
    document.body.style.overflow = '';
  }
  function init() {
    sidebar    = document.getElementById('sidebar');
    backdrop   = document.getElementById('sidebar-backdrop');
    hamburger  = document.getElementById('topbar-hamburger');
    hamburger?.addEventListener('click', open);
    backdrop?.addEventListener('click', close);
    document.addEventListener('keydown', e => { if (e.key === 'Escape') close(); });
  }
  return { init, open, close };
})();

/* ─────────────────────────────────────────────────────────────
   ALERT DISMISS
   ───────────────────────────────────────────────────────────── */
const Alerts = (() => {
  function dismiss(el) {
    el.style.opacity = '0';
    el.style.transform = 'translateY(-8px)';
    el.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
    setTimeout(() => el.remove(), 320);
  }
  function init() {
    document.querySelectorAll('.alert-close').forEach(btn => {
      btn.addEventListener('click', () => dismiss(btn.closest('.alert')));
    });
    // Auto-dismiss after 5s
    document.querySelectorAll('.alert').forEach(el => {
      setTimeout(() => { if (el.isConnected) dismiss(el); }, 5200);
    });
  }
  return { init };
})();

/* ─────────────────────────────────────────────────────────────
   PAGE LOADER
   ───────────────────────────────────────────────────────────── */
const Loader = (() => {
  let loader;
  function show(msg = 'Processing…') {
    loader = document.getElementById('page-loader');
    if (!loader) return;
    loader.querySelector('.loader-msg').textContent = msg;
    loader.classList.add('active');
  }
  function hide() { loader?.classList.remove('active'); }
  function init() {
    document.querySelectorAll('[data-loading]').forEach(form => {
      form.addEventListener('submit', () => show('Analyzing resume…'));
    });
  }
  return { init, show, hide };
})();

/* ─────────────────────────────────────────────────────────────
   PROGRESS BARS (animate on load)
   ───────────────────────────────────────────────────────────── */
const ProgressBars = (() => {
  function init() {
    const bars = document.querySelectorAll('.progress-fill[data-pct]');
    if (!bars.length) return;

    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        const bar = entry.target;
        const pct = parseInt(bar.dataset.pct) || 0;
        // Apply color class
        if (pct >= 75) bar.classList.add('pf-success');
        else if (pct >= 50) {} // default purple
        else if (pct >= 30) bar.classList.add('pf-warning');
        else bar.classList.add('pf-danger');

        requestAnimationFrame(() => { bar.style.width = pct + '%'; });
        observer.unobserve(bar);
      });
    }, { threshold: 0.1 });

    bars.forEach(bar => { bar.style.width = '0'; observer.observe(bar); });
  }
  return { init };
})();

/* ─────────────────────────────────────────────────────────────
   SCORE RINGS (SVG circular progress)
   ───────────────────────────────────────────────────────────── */
const ScoreRings = (() => {
  function buildRing(container, score) {
    const R    = 54;
    const CIRC = 2 * Math.PI * R;
    const pct  = Math.min(Math.max(parseInt(score) || 0, 0), 100);
    const offset = CIRC - (pct / 100) * CIRC;

    const color = pct >= 75 ? '#10b981' : pct >= 50 ? '#6366f1' : pct >= 30 ? '#f59e0b' : '#ef4444';

    container.innerHTML = `
      <div class="score-ring" style="width:130px;height:130px;position:relative;display:flex;align-items:center;justify-content:center">
        <svg viewBox="0 0 120 120" style="position:absolute;inset:0;transform:rotate(-90deg)" xmlns="http://www.w3.org/2000/svg">
          <circle cx="60" cy="60" r="${R}" fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="10"/>
          <circle class="ring-arc" cx="60" cy="60" r="${R}" fill="none"
            stroke="${color}" stroke-width="10" stroke-linecap="round"
            stroke-dasharray="${CIRC}" stroke-dashoffset="${CIRC}"
            style="transition:stroke-dashoffset 1.2s cubic-bezier(0.34,1.2,0.64,1)"/>
        </svg>
        <div style="text-align:center;z-index:1">
          <div style="font-family:var(--font-display);font-size:2rem;font-weight:800;color:#fff;line-height:1">${pct}</div>
          <div style="font-size:11px;color:rgba(255,255,255,0.5);font-weight:600">/100</div>
        </div>
      </div>`;

    const arc = container.querySelector('.ring-arc');
    setTimeout(() => { arc.style.strokeDashoffset = offset; }, 200);
  }

  function init() {
    document.querySelectorAll('[data-score-ring]').forEach(el => {
      const score = el.dataset.scoreRing;
      buildRing(el, score);
    });
  }
  return { init };
})();

/* ─────────────────────────────────────────────────────────────
   DRAG & DROP UPLOAD
   ───────────────────────────────────────────────────────────── */
const Uploader = (() => {
  function init() {
    const zone  = document.getElementById('upload-zone');
    const input = document.getElementById('file-input');
    if (!zone || !input) return;

    zone.addEventListener('click', () => input.click());

    zone.addEventListener('dragover', e => {
      e.preventDefault();
      zone.classList.add('drag-over');
    });
    zone.addEventListener('dragleave', e => {
      if (!zone.contains(e.relatedTarget)) zone.classList.remove('drag-over');
    });
    zone.addEventListener('drop', e => {
      e.preventDefault();
      zone.classList.remove('drag-over');
      const file = e.dataTransfer.files[0];
      if (file) updateFile(file);
    });

    input.addEventListener('change', () => {
      if (input.files[0]) updateFile(input.files[0]);
    });

    function updateFile(file) {
      const dt = new DataTransfer();
      dt.items.add(file);
      input.files = dt.files;

      const nameEl = document.getElementById('file-name-display');
      if (nameEl) nameEl.textContent = file.name;

      const sizeEl = document.getElementById('file-size-display');
      if (sizeEl) sizeEl.textContent = formatBytes(file.size);

      const preview = document.getElementById('upload-preview');
      if (preview) { preview.style.display = 'flex'; }

      const icon = zone.querySelector('.upload-icon-ring i');
      if (icon) {
        icon.className = 'fa-solid fa-circle-check';
        icon.style.color = 'var(--clr-success)';
      }
      zone.style.borderColor = 'var(--clr-success)';
      zone.style.background  = 'rgba(16,185,129,0.04)';
    }
  }

  function formatBytes(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / 1048576).toFixed(1) + ' MB';
  }

  return { init };
})();

/* ─────────────────────────────────────────────────────────────
   TABLE SEARCH (live filter)
   ───────────────────────────────────────────────────────────── */
const TableSearch = (() => {
  function init() {
    const input = document.getElementById('table-search');
    if (!input) return;
    input.addEventListener('input', () => {
      const q = input.value.toLowerCase().trim();
      const targets = document.querySelectorAll('tbody tr, .job-card, .card[data-searchable]');
      targets.forEach(el => {
        el.style.display = el.textContent.toLowerCase().includes(q) ? '' : 'none';
      });
    });
  }
  return { init };
})();

/* ─────────────────────────────────────────────────────────────
   CONFIRM DIALOGS
   ───────────────────────────────────────────────────────────── */
const Confirm = (() => {
  function init() {
    document.querySelectorAll('[data-confirm]').forEach(el => {
      el.addEventListener('click', e => {
        if (!confirm(el.dataset.confirm)) e.preventDefault();
      });
    });
  }
  return { init };
})();

/* ─────────────────────────────────────────────────────────────
   INTERSECTION OBSERVER (scroll animations)
   ───────────────────────────────────────────────────────────── */
const ScrollAnims = (() => {
  function init() {
    const observer = new IntersectionObserver(entries => {
      entries.forEach(e => {
        if (e.isIntersecting) {
          e.target.style.opacity   = '1';
          e.target.style.transform = 'translateY(0)';
          observer.unobserve(e.target);
        }
      });
    }, { threshold: 0.08 });

    document.querySelectorAll('.scroll-reveal').forEach(el => {
      el.style.opacity   = '0';
      el.style.transform = 'translateY(18px)';
      el.style.transition= 'opacity 0.5s ease, transform 0.5s ease';
      observer.observe(el);
    });
  }
  return { init };
})();

/* ─────────────────────────────────────────────────────────────
   COUNTER ANIMATION (stat numbers)
   ───────────────────────────────────────────────────────────── */
const Counters = (() => {
  function animateCount(el, target, duration = 900) {
    const start = performance.now();
    const from  = 0;
    function tick(now) {
      const elapsed = now - start;
      const progress = Math.min(elapsed / duration, 1);
      const ease = 1 - Math.pow(1 - progress, 3); // ease-out-cubic
      el.textContent = Math.round(from + (target - from) * ease);
      if (progress < 1) requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  }

  function init() {
    const observer = new IntersectionObserver(entries => {
      entries.forEach(e => {
        if (!e.isIntersecting) return;
        const el = e.target;
        const target = parseInt(el.dataset.count) || 0;
        animateCount(el, target);
        observer.unobserve(el);
      });
    }, { threshold: 0.3 });

    document.querySelectorAll('[data-count]').forEach(el => observer.observe(el));
  }
  return { init };
})();

/* ─────────────────────────────────────────────────────────────
   TOOLTIP (simple title-based)
   ───────────────────────────────────────────────────────────── */
const Tooltip = (() => {
  function init() {
    document.querySelectorAll('[data-tip]').forEach(el => {
      el.title = el.dataset.tip;
    });
  }
  return { init };
})();

/* ─────────────────────────────────────────────────────────────
   AUTO-SUBMIT STATUS SELECTS
   ───────────────────────────────────────────────────────────── */
const AutoSubmit = (() => {
  function init() {
    document.querySelectorAll('select[data-auto-submit]').forEach(sel => {
      sel.addEventListener('change', () => sel.closest('form')?.submit());
    });
  }
  return { init };
})();

/* ─────────────────────────────────────────────────────────────
   SMOOTH PAGE TRANSITIONS (subtle)
   ───────────────────────────────────────────────────────────── */
const PageTransition = (() => {
  function init() {
    document.querySelectorAll('a:not([target="_blank"]):not([href^="#"]):not([href^="mailto"])').forEach(a => {
      a.addEventListener('click', e => {
        if (e.ctrlKey || e.metaKey || e.shiftKey) return;
        const href = a.getAttribute('href');
        if (!href || href === '#' || href.startsWith('javascript')) return;
        // Very subtle — just ensure page-body fades
        const body = document.querySelector('.page-body');
        if (body) { body.style.opacity = '0'; body.style.transition = 'opacity 0.15s ease'; }
      });
    });
  }
  return { init };
})();

/* ─────────────────────────────────────────────────────────────
   PASSWORD VISIBILITY TOGGLE
   ───────────────────────────────────────────────────────────── */
const PasswordToggle = (() => {
  function init() {
    document.querySelectorAll('.btn-pwd-toggle').forEach(btn => {
      btn.addEventListener('click', () => {
        const input = btn.previousElementSibling;
        if (!input) return;
        const isText = input.type === 'text';
        input.type = isText ? 'password' : 'text';
        btn.querySelector('i').className = isText ? 'fa-solid fa-eye' : 'fa-solid fa-eye-slash';
      });
    });
  }
  return { init };
})();

/* Demo account autofill */
const DemoLogin = (() => {
  function init() {
    const emailInput = document.getElementById('login-email');
    const passwordInput = document.getElementById('login-password');
    if (!emailInput || !passwordInput) return;

    document.querySelectorAll('.demo-login-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        emailInput.value = btn.dataset.demoEmail || '';
        passwordInput.value = btn.dataset.demoPassword || '';
        emailInput.dispatchEvent(new Event('input', { bubbles: true }));
        passwordInput.dispatchEvent(new Event('input', { bubbles: true }));
        emailInput.focus();
      });
    });
  }
  return { init };
})();

/* ─────────────────────────────────────────────────────────────
   INITIALIZE ALL
   ───────────────────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  Sidebar.init();
  Alerts.init();
  Loader.init();
  ProgressBars.init();
  ScoreRings.init();
  Uploader.init();
  TableSearch.init();
  Confirm.init();
  ScrollAnims.init();
  Counters.init();
  Tooltip.init();
  AutoSubmit.init();
  PasswordToggle.init();
  DemoLogin.init();

  // Fade in page body
  const body = document.querySelector('.page-body');
  if (body) {
    body.style.opacity = '0';
    body.style.transition = 'opacity 0.3s ease';
    requestAnimationFrame(() => { body.style.opacity = '1'; });
  }
});
