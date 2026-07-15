/* The Mother's Code — interactions
   Scroll reveal · nav state · hero parallax · floating gold particles.
   Vanilla JS, no dependencies. Respects prefers-reduced-motion. */
(function () {
  "use strict";
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ================= PADDLE CHECKOUT CONFIG =================
     Production is always the default so this can never accidentally ship
     sandbox credentials live. Append ?paddle_test=1 to the URL to opt into
     sandbox mode for manual testing (e.g. on a staging preview deploy) —
     never flip PRODUCTION defaults below to sandbox values directly.    */
  var USE_SANDBOX = /[?&]paddle_test=1(&|$)/.test(window.location.search);

  var PADDLE_ENV = USE_SANDBOX ? "sandbox" : "production";
  var PADDLE_CLIENT_TOKEN = USE_SANDBOX
    ? "test_4a93e21107691b36c821cd04e19"
    : "live_dcce5b904c3ae5f702f171e70cc";
  var PADDLE_PRICE_ID = USE_SANDBOX
    ? "pri_01kxj12733fxd2qmrhaxvfmyv0"
    : "pri_01kxdcfq1eppngwvzvz68fesvq";
  /* =========================================================== */

  var paddleReady = false;
  if (window.Paddle && PADDLE_CLIENT_TOKEN && PADDLE_PRICE_ID) {
    try {
      if (PADDLE_ENV === "sandbox") window.Paddle.Environment.set("sandbox");
      window.Paddle.Initialize({ token: PADDLE_CLIENT_TOKEN });
      paddleReady = true;
    } catch (e) { /* fall through to the not-ready fallback */ }
  }

  function openCheckout() {
    if (paddleReady) {
      window.Paddle.Checkout.open({
        items: [{ priceId: PADDLE_PRICE_ID, quantity: 1 }],
        settings: {
          displayMode: "overlay",
          successUrl: "https://www.the-mothers-code.com/thank-you.html"
        }
      });
    } else {
      // checkout not yet configured — take orders by email instead of failing silently
      window.location.href =
        "mailto:contact@the-mothers-code.com?subject=Order%20The%20Mother%27s%20Code" +
        "&body=Hi%2C%20I%27d%20like%20to%20order%20the%20PDF%20edition%20(%2414.99).";
    }
  }

  document.querySelectorAll(".js-buy").forEach(function (el) {
    el.addEventListener("click", function (ev) {
      ev.preventDefault();
      openCheckout();
    });
  });

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

  /* ---- sticky buy button ----
     Appears once the visitor scrolls past the hero's own CTA, hides while
     the final #buy section (which already has a CTA) is in view.
     Rect-based like the reveal system above, not IntersectionObserver —
     some embedded webviews don't fire IO reliably here. */
  var stickyBuy = document.getElementById("stickyBuy");
  var heroSection = document.getElementById("top");
  var buySection = document.getElementById("buy");
  if (stickyBuy && heroSection && buySection) {
    var setStickyVisible = function (visible) {
      stickyBuy.classList.toggle("is-visible", visible);
      stickyBuy.setAttribute("aria-hidden", visible ? "false" : "true");
      stickyBuy.tabIndex = visible ? 0 : -1;
    };
    var updateSticky = function () {
      var vh = window.innerHeight || document.documentElement.clientHeight;
      var pastHero = heroSection.getBoundingClientRect().bottom < 0;
      var buyRect = buySection.getBoundingClientRect();
      var buyInView = buyRect.top < vh && buyRect.bottom > 0;
      setStickyVisible(pastHero && !buyInView);
    };
    updateSticky();
    window.addEventListener("scroll", updateSticky, { passive: true });
    window.addEventListener("resize", updateSticky, { passive: true });
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
