/* paolopecere.it — small enhancements. The site works without this file. */
(function () {
  'use strict';

  /* header: transparent over the photograph, solid once the page scrolls */
  var header = document.querySelector('.site-header');
  if (header) {
    var setStuck = function () {
      header.classList.toggle('is-stuck', window.scrollY > 24 && !header.classList.contains('nav-open'));
    };
    setStuck();
    window.addEventListener('scroll', setStuck, { passive: true });

    /* small screens: menu button */
    var toggle = header.querySelector('.menu-toggle');
    if (toggle) {
      var setOpen = function (open) {
        header.classList.toggle('nav-open', open);
        toggle.setAttribute('aria-expanded', String(open));
        toggle.textContent = open ? toggle.dataset.close : toggle.dataset.open;
        document.documentElement.style.overflow = open ? 'hidden' : '';
        setStuck();
      };
      toggle.addEventListener('click', function () { setOpen(!header.classList.contains('nav-open')); });
      document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && header.classList.contains('nav-open')) { setOpen(false); toggle.focus(); } });
      window.matchMedia('(min-width: 62.01rem)').addEventListener('change', function (m) { if (m.matches) setOpen(false); });
    }
  }

  /* lists: search box and outlet buttons */
  document.querySelectorAll('[data-filter]').forEach(function (root) {
    var input = root.querySelector('[data-filter-input]');
    var buttons = Array.prototype.slice.call(root.querySelectorAll('[data-filter-outlet]'));
    var entries = Array.prototype.slice.call(root.querySelectorAll('[data-entry]'));
    var groups = Array.prototype.slice.call(root.querySelectorAll('[data-group]'));
    var count = root.querySelector('[data-filter-count]');
    var empty = root.querySelector('[data-filter-empty]');
    var outlet = '';
    var norm = function (s) { return s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, ''); };
    var texts = entries.map(function (el) { return norm(el.textContent); });

    var apply = function () {
      var words = input ? norm(input.value).split(/\s+/).filter(Boolean) : [];
      var shown = 0;
      entries.forEach(function (el, i) {
        var ok = (!outlet || el.dataset.outlet === outlet) && words.every(function (w) { return texts[i].indexOf(w) !== -1; });
        el.hidden = !ok;
        if (ok) shown++;
      });
      groups.forEach(function (g) { g.hidden = !g.querySelector('[data-entry]:not([hidden])'); });
      if (count) count.textContent = count.dataset.template.replace('{n}', shown);
      if (empty) empty.hidden = shown !== 0;
    };
    if (input) input.addEventListener('input', apply);
    buttons.forEach(function (b) {
      b.addEventListener('click', function () {
        outlet = b.dataset.filterOutlet;
        buttons.forEach(function (x) { x.setAttribute('aria-pressed', String(x === b)); });
        apply();
      });
    });
  });

  /* events: decide what is upcoming with today's date, so the page stays right between updates */
  var pad = function (n) { return (n < 10 ? '0' : '') + n; };
  var now = new Date();
  var today = now.getFullYear() + '-' + pad(now.getMonth() + 1) + '-' + pad(now.getDate());
  document.querySelectorAll('[data-events]').forEach(function (root) {
    var upcoming = root.querySelector('[data-events-upcoming]');
    var past = root.querySelector('[data-events-past]');
    var none = root.querySelector('[data-events-none]');
    var pastSection = root.querySelector('[data-events-past-section]');
    var items = Array.prototype.slice.call(root.querySelectorAll('[data-event-end]'));
    items.forEach(function (el) {
      var isPast = el.dataset.eventEnd < today;
      if (isPast && upcoming && past && el.parentNode === upcoming) past.insertBefore(el, past.firstChild);
      if (!isPast && upcoming && past && el.parentNode === past) upcoming.appendChild(el);
    });
    if (upcoming && past) {
      var byDate = function (dir) { return function (a, b) { return dir * a.dataset.eventStart.localeCompare(b.dataset.eventStart); }; };
      Array.prototype.slice.call(upcoming.children).sort(byDate(1)).forEach(function (el) { upcoming.appendChild(el); });
      Array.prototype.slice.call(past.children).sort(byDate(-1)).forEach(function (el) { past.appendChild(el); });
      if (none) none.hidden = upcoming.children.length !== 0;
      if (pastSection) pastSection.hidden = past.children.length === 0;
    }
  });
  /* home page: show only events that are still to come, and hide the block when there are none */
  document.querySelectorAll('[data-events-teaser]').forEach(function (root) {
    var left = 0;
    root.querySelectorAll('[data-event-end]').forEach(function (el) {
      var keep = el.dataset.eventEnd >= today && left < 3;
      el.hidden = !keep;
      if (keep) left++;
    });
    root.hidden = left === 0;
  });
})();
