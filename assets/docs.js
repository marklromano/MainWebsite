/* Docs search and "on this page" highlighting. First-party, runs offline, sends nothing anywhere.
   The pages work without it: the search box only appears when this script runs. */
(function () {
  "use strict";

  var box = document.querySelector(".docs-search");
  var input = document.getElementById("docs-q");
  var results = document.getElementById("docs-results");
  var index = window.DOCS_INDEX || [];

  if (box && input && results && index.length) {
    box.hidden = false;
    var active = -1;

    var escapeHtml = function (s) {
      return s.replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; });
    };
    var mark = function (text, terms) {
      var out = escapeHtml(text);
      terms.forEach(function (t) {
        out = out.replace(new RegExp("(" + t.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + ")", "ig"), "<mark>$1</mark>");
      });
      return out;
    };
    var snippet = function (text, terms) {
      var lower = text.toLowerCase();
      var at = lower.indexOf(terms[0]);
      if (at < 0) { return text.slice(0, 140); }
      var start = Math.max(0, at - 50);
      return (start > 0 ? "…" : "") + text.slice(start, start + 150) + (start + 150 < text.length ? "…" : "");
    };

    var search = function (q) {
      var terms = q.toLowerCase().split(/\s+/).filter(Boolean);
      if (!terms.length) { return []; }
      var hits = [];
      index.forEach(function (e) {
        var h = e.h.toLowerCase(), p = e.p.toLowerCase(), x = e.x.toLowerCase();
        var score = 0;
        for (var i = 0; i < terms.length; i++) {
          var t = terms[i], s = 0;
          if (h.indexOf(t) >= 0) { s += 10; }
          if (p.indexOf(t) >= 0) { s += 4; }
          if (x.indexOf(t) >= 0) { s += 1; }
          if (!s) { return; }
          score += s;
        }
        hits.push({ e: e, score: score });
      });
      hits.sort(function (a, b) { return b.score - a.score; });
      return hits.slice(0, 8).map(function (hit) { return hit.e; });
    };

    var render = function () {
      var q = input.value.trim();
      var terms = q.toLowerCase().split(/\s+/).filter(Boolean);
      active = -1;
      if (!q) { results.hidden = true; results.innerHTML = ""; return; }
      var hits = search(q);
      if (!hits.length) {
        results.innerHTML = '<p class="docs-noresult">Nothing found for “' + escapeHtml(q) + '”. Try another word, or ask on the support page.</p>';
      } else {
        results.innerHTML = hits.map(function (e, i) {
          var where = e.h === e.p ? e.p : e.p + " › " + e.h;
          return '<a role="option" id="docs-r' + i + '" href="' + e.u + '"><strong>' + mark(where, terms) + "</strong><span>" +
            mark(snippet(e.x, terms), terms) + "</span></a>";
        }).join("");
      }
      results.hidden = false;
    };

    var move = function (step) {
      var links = results.querySelectorAll("a");
      if (!links.length) { return; }
      active = (active + step + links.length) % links.length;
      links.forEach(function (a, i) { a.classList.toggle("is-active", i === active); });
      links[active].scrollIntoView({ block: "nearest" });
    };

    input.addEventListener("input", render);
    input.addEventListener("keydown", function (ev) {
      if (ev.key === "ArrowDown") { ev.preventDefault(); move(1); }
      else if (ev.key === "ArrowUp") { ev.preventDefault(); move(-1); }
      else if (ev.key === "Enter") {
        var links = results.querySelectorAll("a");
        if (links.length) { ev.preventDefault(); window.location.href = links[Math.max(active, 0)].getAttribute("href"); }
      } else if (ev.key === "Escape") { input.value = ""; render(); input.blur(); }
    });
    document.addEventListener("keydown", function (ev) {
      var typing = /INPUT|TEXTAREA|SELECT/.test(document.activeElement.tagName);
      if (ev.key === "/" && !typing) { ev.preventDefault(); input.focus(); }
    });
    document.addEventListener("click", function (ev) {
      if (!box.contains(ev.target)) { results.hidden = true; }
    });
    input.addEventListener("focus", function () { if (input.value.trim()) { render(); } });
  }

  // "On this page": highlight the section being read
  var toc = document.querySelectorAll(".docs-toc a");
  if (toc.length && "IntersectionObserver" in window) {
    var byId = {};
    toc.forEach(function (a) { byId[decodeURIComponent(a.getAttribute("href").slice(1))] = a; });
    var headings = Array.prototype.filter.call(document.querySelectorAll(".prose h2[id], .prose h3[id]"),
      function (h) { return byId[h.id]; });
    var current = null;
    var observer = new IntersectionObserver(function () {
      var top = null;
      headings.forEach(function (h) { if (h.getBoundingClientRect().top < 140) { top = h; } });
      top = top || headings[0];
      if (top !== current) {
        if (current) { byId[current.id].classList.remove("is-current"); }
        byId[top.id].classList.add("is-current");
        current = top;
      }
    }, { rootMargin: "0px 0px -70% 0px", threshold: [0, 1] });
    headings.forEach(function (h) { observer.observe(h); });
  }
})();
