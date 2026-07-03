/* The Mother's Code — interactions
   Scroll reveal · nav state · hero parallax · floating gold particles.
   Vanilla JS, no dependencies. Respects prefers-reduced-motion. */
(function () {
  "use strict";
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---- nav background on scroll ---- */
  var nav = document.getElementById("nav");
  function onScrollNav() {
    if (window.scrollY > 24) nav.classList.add("scrolled");
    else nav.classList.remove("scrolled");
  }
  onScrollNav();
  window.addEventListener("scroll", onScrollNav, { passive: true });

  /* ---- scroll reveal (fade + slide up) ----
     Rect-based rather than IntersectionObserver: some embedded webviews
     don't fire IO for already-visible elements, which would leave the hero
     stuck invisible. This checks position on load + scroll, with a hard
     safety net so content can never remain hidden. */
  var revealEls = Array.prototype.slice.call(document.querySelectorAll(".reveal"));
  function revealInView() {
    var vh = window.innerHeight || document.documentElement.clientHeight;
    for (var i = revealEls.length - 1; i >= 0; i--) {
      var el = revealEls[i];
      var top = el.getBoundingClientRect().top;
      if (top < vh * 0.9) {
        el.classList.add("in");
        revealEls.splice(i, 1);
      }
    }
  }
  if (reduce) {
    revealEls.forEach(function (el) { el.classList.add("in"); });
    revealEls.length = 0;
  } else {
    revealInView();
    window.addEventListener("scroll", revealInView, { passive: true });
    window.addEventListener("resize", revealInView, { passive: true });
    // safety net: never leave anything permanently hidden
    setTimeout(function () {
      document.querySelectorAll(".reveal:not(.in)").forEach(function (el) {
        var t = el.getBoundingClientRect().top;
        if (t < (window.innerHeight || 0)) el.classList.add("in");
      });
    }, 1200);
  }

  /* ---- subtle hero parallax ---- */
  var parallax = document.querySelector("[data-parallax]");
  if (parallax && !reduce) {
    window.addEventListener("scroll", function () {
      var y = window.scrollY;
      if (y < window.innerHeight) parallax.style.transform = "translateY(" + y * 0.18 + "px)";
    }, { passive: true });
  }

  /* ---- floating gold particles ---- */
  function seedParticles(container, count) {
    if (!container || reduce) return;
    for (var i = 0; i < count; i++) {
      var p = document.createElement("span");
      p.className = "particle";
      var size = 3 + Math.random() * 8;
      p.style.width = size + "px";
      p.style.height = size + "px";
      p.style.left = Math.random() * 100 + "%";
      p.style.bottom = "-10px";
      p.style.animationDuration = (7 + Math.random() * 9) + "s";
      p.style.animationDelay = (Math.random() * 8) + "s";
      container.appendChild(p);
    }
  }
  seedParticles(document.getElementById("particles"), 16);
  seedParticles(document.getElementById("ctaParticles"), 14);
})();
