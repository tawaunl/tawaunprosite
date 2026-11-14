(function () {
  'use strict';
  document.documentElement.classList.add('js');

  /* ---------- mobile nav ---------- */
  var toggle = document.querySelector('.navbar__toggle');
  var menu = document.getElementById('menu');
  if (toggle && menu) {
    toggle.addEventListener('click', function () {
      var open = menu.classList.toggle('open');
      toggle.setAttribute('aria-expanded', String(open));
    });
    menu.addEventListener('click', function (e) {
      if (e.target.tagName === 'A') { menu.classList.remove('open'); toggle.setAttribute('aria-expanded', 'false'); }
    });
  }

  /* ---------- cite modal ---------- */
  var dataEl = document.getElementById('bibtex-data');
  var bib = dataEl ? JSON.parse(dataEl.textContent) : {};
  var modal = document.getElementById('cite-modal');
  var code = document.getElementById('cite-code');
  var dl = document.getElementById('cite-download');
  var copyBtn = document.getElementById('cite-copy');
  var lastFocus = null;

  function openCite(slug) {
    var text = bib[slug];
    if (!text) return;
    code.textContent = text;
    dl.href = URL.createObjectURL(new Blob([text], { type: 'text/plain' }));
    dl.download = slug + '.bib';
    lastFocus = document.activeElement;
    modal.hidden = false;
    modal.querySelector('.modal__close').focus();
  }
  function closeCite() {
    modal.hidden = true;
    copyBtn.innerHTML = '<i class="fas fa-copy"></i> Copy';
    if (lastFocus) lastFocus.focus();
  }
  document.addEventListener('click', function (e) {
    var btn = e.target.closest('.js-cite');
    if (btn) { e.preventDefault(); openCite(btn.dataset.slug); }
  });
  if (modal) {
    modal.addEventListener('click', function (e) {
      if (e.target === modal || e.target.closest('.modal__close')) closeCite();
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && !modal.hidden) closeCite();
    });
    copyBtn.addEventListener('click', function () {
      var text = code.textContent;
      var done = function () { copyBtn.innerHTML = '<i class="fas fa-check"></i> Copied'; };
      if (navigator.clipboard) navigator.clipboard.writeText(text).then(done, function () {});
      else {
        var r = document.createRange(); r.selectNodeContents(code);
        var s = window.getSelection(); s.removeAllRanges(); s.addRange(r);
        try { document.execCommand('copy'); done(); } catch (err) {}
      }
    });
  }

  /* ---------- publication filters ---------- */
  var list = document.getElementById('pub-list');
  if (list) {
    var items = Array.prototype.slice.call(list.querySelectorAll('.pub-list-item'));
    var search = document.getElementById('pub-search');
    var type = document.getElementById('pub-type');
    var year = document.getElementById('pub-year');
    var empty = document.getElementById('pub-empty');
    var apply = function () {
      var q = search.value.trim().toLowerCase();
      var shown = 0;
      items.forEach(function (it) {
        var ok = (!q || it.textContent.toLowerCase().indexOf(q) !== -1) &&
          (type.value === '*' || it.dataset.type === type.value) &&
          (year.value === '*' || it.dataset.year === year.value);
        it.hidden = !ok;
        if (ok) shown++;
      });
      empty.hidden = shown !== 0;
    };
    search.addEventListener('input', apply);
    type.addEventListener('change', apply);
    year.addEventListener('change', apply);
  }

  /* ---------- skill circles fill on scroll ---------- */
  var circles = document.querySelectorAll('.circle');
  if (circles.length) {
    if ('IntersectionObserver' in window && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add('is-in'); io.unobserve(en.target); } });
      }, { threshold: 0.4 });
      circles.forEach(function (c) { io.observe(c); });
    } else {
      circles.forEach(function (c) { c.classList.add('is-in'); });
    }
  }
})();
