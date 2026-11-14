(function () {
  'use strict';
  var root = document.documentElement;
  root.classList.add('js');
  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- year ---------- */
  var y = document.getElementById('year');
  if (y) y.textContent = new Date().getFullYear();

  /* ---------- theme toggle ---------- */
  var darkQuery = window.matchMedia('(prefers-color-scheme: dark)');
  function isDark() {
    var t = root.dataset.theme;
    return t ? t === 'dark' : darkQuery.matches;
  }
  var toggle = document.getElementById('theme-toggle');
  if (toggle) {
    toggle.addEventListener('click', function () {
      var next = isDark() ? 'light' : 'dark';
      root.dataset.theme = next;
      try { localStorage.setItem('theme', next); } catch (e) {}
      if (field) field.recolor();
    });
  }
  darkQuery.addEventListener && darkQuery.addEventListener('change', function () { if (field) field.recolor(); });

  /* ---------- nav ---------- */
  var nav = document.querySelector('.nav');
  var navToggle = document.querySelector('.nav__toggle');
  var navLinks = document.getElementById('nav-links');
  if (navToggle) {
    navToggle.addEventListener('click', function () {
      var open = navToggle.getAttribute('aria-expanded') === 'true';
      navToggle.setAttribute('aria-expanded', String(!open));
      navLinks.classList.toggle('is-open', !open);
    });
    navLinks.addEventListener('click', function (e) {
      if (e.target.tagName === 'A') {
        navToggle.setAttribute('aria-expanded', 'false');
        navLinks.classList.remove('is-open');
      }
    });
  }
  function onScroll() { nav.classList.toggle('is-scrolled', window.scrollY > 8); }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /* active section highlight */
  var links = Array.prototype.slice.call(document.querySelectorAll('.nav__links a'));
  if ('IntersectionObserver' in window) {
    var byId = {};
    links.forEach(function (a) { byId[a.getAttribute('href').slice(1)] = a; });
    var spy = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting && byId[en.target.id]) {
          links.forEach(function (a) { a.classList.remove('is-active'); });
          byId[en.target.id].classList.add('is-active');
        }
      });
    }, { rootMargin: '-45% 0px -50% 0px' });
    Object.keys(byId).forEach(function (id) { var s = document.getElementById(id); if (s) spy.observe(s); });
  }

  /* ---------- reveal ---------- */
  var reveals = document.querySelectorAll('.reveal');
  if (!reduceMotion && 'IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add('is-in'); io.unobserve(en.target); }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.05 });
    reveals.forEach(function (el) { io.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add('is-in'); });
  }

  /* ---------- publication filters ---------- */
  var filters = document.querySelectorAll('.filter');
  var pubs = document.querySelectorAll('.publist li');
  filters.forEach(function (btn) {
    btn.addEventListener('click', function () {
      var f = btn.dataset.filter;
      filters.forEach(function (b) {
        var on = b === btn;
        b.classList.toggle('is-active', on);
        b.setAttribute('aria-pressed', String(on));
      });
      pubs.forEach(function (li) {
        var tags = (li.dataset.tags || '').split(' ');
        li.hidden = f !== 'all' && tags.indexOf(f) === -1;
      });
    });
  });

  /* ---------- hero: drifting single-cell embedding ---------- */
  var field = (function () {
    var canvas = document.querySelector('.hero__field');
    if (!canvas || !canvas.getContext) return null;
    var ctx = canvas.getContext('2d');
    var hero = canvas.parentElement;
    var W = 0, H = 0, dpr = 1, pts = [], colors = [], raf = 0, visible = true, t0 = performance.now();
    var mouse = { x: -1e4, y: -1e4 };

    // Seeded RNG so the "embedding" looks the same on every visit.
    var seed = 7;
    function rand() { seed = (seed * 16807) % 2147483647; return (seed - 1) / 2147483646; }
    function gauss() { var u = rand() || 1e-9, v = rand(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); }

    // Cluster centres in normalized space (x biased right, behind the portrait).
    var clusters = [
      { x: .74, y: .22, sx: .055, sy: .045, r: -.5, n: 1.0 },
      { x: .90, y: .44, sx: .040, sy: .075, r: .3,  n: .8 },
      { x: .68, y: .70, sx: .060, sy: .040, r: .6,  n: 1.1 },
      { x: .86, y: .80, sx: .050, sy: .045, r: -.2, n: .7 },
      { x: .96, y: .16, sx: .030, sy: .040, r: 0,   n: .45 },
      { x: .62, y: .40, sx: .030, sy: .050, r: .9,  n: .5 }
    ];

    function readColors() {
      var cs = getComputedStyle(root);
      colors = ['--c1', '--c2', '--c3', '--c4', '--c5', '--c6'].map(function (v) { return cs.getPropertyValue(v).trim() || '#888'; });
    }

    function build() {
      seed = 7; pts = [];
      var total = W < 700 ? 360 : 820;
      var weight = clusters.reduce(function (s, c) { return s + c.n; }, 0);
      clusters.forEach(function (c, ci) {
        var n = Math.round(total * c.n / weight);
        var cos = Math.cos(c.r), sin = Math.sin(c.r);
        for (var i = 0; i < n; i++) {
          // two sub-lobes per cluster give irregular, organic shapes
          var lobe = rand() < .35 ? 1 : 0;
          var gx = gauss() * c.sx * (lobe ? .6 : 1) + (lobe ? c.sx * 1.2 : 0);
          var gy = gauss() * c.sy * (lobe ? .6 : 1) + (lobe ? c.sy * .4 : 0);
          var x = c.x + gx * cos - gy * sin;
          var y = c.y + gx * sin + gy * cos;
          pts.push({ hx: x, hy: y, x: x, y: y, c: ci, r: .9 + rand() * 1.5, p: rand() * 6.283, s: .3 + rand() * .7, a: .35 + rand() * .5 });
        }
      });
      // sparse background "noise" cells
      for (var k = 0; k < total * .08; k++) {
        var bx = .5 + rand() * .5, by = rand();
        pts.push({ hx: bx, hy: by, x: bx, y: by, c: Math.floor(rand() * 6), r: .8 + rand(), p: rand() * 6.283, s: .2 + rand() * .4, a: .2 + rand() * .2 });
      }
    }

    function resize() {
      var rect = hero.getBoundingClientRect();
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      W = rect.width; H = rect.height;
      canvas.width = Math.round(W * dpr); canvas.height = Math.round(H * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      var wasSmall = pts.length && pts.length < 500;
      if (!pts.length || wasSmall !== (W < 700)) build();
      draw(performance.now());
    }

    function draw(now) {
      var t = (now - t0) / 1000;
      ctx.clearRect(0, 0, W, H);
      // On narrow screens, spread the cloud across full width.
      var narrow = W < 860;
      var ox = narrow ? -.25 * W : 0, sx = narrow ? 1.35 * W : W;
      for (var i = 0; i < pts.length; i++) {
        var p = pts[i];
        var px = ox + (p.hx + Math.sin(t * .35 * p.s + p.p) * .006) * sx;
        var py = (p.hy + Math.cos(t * .3 * p.s + p.p * 1.3) * .008) * H;
        var dx = px - mouse.x, dy = py - mouse.y, d2 = dx * dx + dy * dy;
        if (d2 < 12000) { var f = (1 - d2 / 12000) * 18 / Math.sqrt(d2 + 1); px += dx * f * .35; py += dy * f * .35; }
        // ease toward target for smooth mouse interaction
        p.x += (px - p.x) * .12; p.y += (py - p.y) * .12;
        ctx.globalAlpha = p.a;
        ctx.fillStyle = colors[p.c];
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, 6.283);
        ctx.fill();
      }
      ctx.globalAlpha = 1;
    }

    function settle() { // place points exactly (no easing) for the static frame
      for (var i = 0; i < 40; i++) draw(t0);
    }

    function loop(now) {
      draw(now);
      raf = visible ? requestAnimationFrame(loop) : 0;
    }

    readColors();
    resize();
    settle();

    if (!reduceMotion) {
      raf = requestAnimationFrame(loop);
      hero.addEventListener('pointermove', function (e) {
        var r = hero.getBoundingClientRect(); mouse.x = e.clientX - r.left; mouse.y = e.clientY - r.top;
      });
      hero.addEventListener('pointerleave', function () { mouse.x = mouse.y = -1e4; });
      if ('IntersectionObserver' in window) {
        new IntersectionObserver(function (en) {
          visible = en[0].isIntersecting;
          if (visible && !raf) raf = requestAnimationFrame(loop);
        }).observe(hero);
      }
    }

    var rt;
    window.addEventListener('resize', function () { clearTimeout(rt); rt = setTimeout(function () { resize(); if (reduceMotion) settle(); }, 120); });

    return {
      recolor: function () { readColors(); if (reduceMotion) settle(); }
    };
  })();
})();
