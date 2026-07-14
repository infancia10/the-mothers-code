/* The Mother's Code — social proof: impact stats, trust badges, engagement
   pills, reviews. Single CONFIG below drives everything on the page.

   Honesty rules baked into this file, on purpose:
   - Approximate numbers (`demo: true`) render with a visible "Demo data"
     tag until replaced with real figures. Exact facts (chapter count) never
     get a "+" suffix, since that would imply an estimate.
   - Average rating, the star breakdown, the recommend line, and the whole
     Reviews section are NEVER faked — they're computed from `reviews` and
     stay honest (a plain "—" / "New release") until that array has real
     entries in it.
   - The "viewed today" / "recommended" pills use qualitative language, not
     a fabricated headcount. */
(function () {
  "use strict";

  var CONFIG = {
    // Large "impact" stats. `value` + `demo: true` = a placeholder that
    // still needs a real number behind it — keep these plausible for an
    // early-stage single-title store, not vanity-scale (a giant "1.2M+"
    // would itself be the misleading claim, tag or no tag). Swap in real
    // Paddle/analytics figures as they exist.
    impactStats: {
      parentsInspired: { icon: "❤️", label: "Parents Inspired", value: 1000, demo: true },
      familiesReached: { icon: "📚", label: "Families Reached", value: 750, demo: true },
      chaptersInside: { icon: "🧠", label: "Research-Based Chapters", value: 21, demo: false }
      // "Average Reader Rating" is computed from `reviews` below, not listed here.
    },
    trustBadges: [
      { icon: "🧠", text: "Research-Informed" },
      { icon: "❤️", text: "Parent-Focused" },
      { icon: "📖", text: "Practical Guidance" },
      { icon: "👶", text: "From Newborn to Early Childhood" },
      { icon: "🌱", text: "Built for Modern Families" }
    ],
    engagement: {
      exploring: { icon: "👀", text: "Parents exploring this guide today" },
      recommended: { icon: "⭐", text: "Recommended parenting resource" }
    },
    // Add real reviews as they come in. Shape:
    // { name: "J.", initials: "J", rating: 5, date: "2026-06-02", text: "...", helpful: 0 }
    // The rating stat, star breakdown, recommend line, and Reviews section
    // all activate/upgrade automatically the moment this array is non-empty.
    reviews: []
  };

  /* ---------------- shared helpers ---------------- */
  function computeAverageRating(reviews) {
    if (!reviews || !reviews.length) return null;
    var sum = reviews.reduce(function (s, r) { return s + r.rating; }, 0);
    return sum / reviews.length;
  }

  function starString(avg) {
    var full = Math.max(0, Math.min(5, Math.round(avg)));
    return "★★★★★".slice(0, full) + "☆☆☆☆☆".slice(0, 5 - full);
  }

  function formatDate(iso) {
    try {
      var d = new Date(iso + "T00:00:00");
      return d.toLocaleDateString(undefined, { year: "numeric", month: "short" });
    } catch (e) { return iso; }
  }

  // 1200000 -> "1.2M+", 850000 -> "850K+", 750 -> "750+". Only for
  // approximate/demo figures — never applied to exact facts like chapter count.
  function formatApproxCount(n) {
    if (n >= 1000000) {
      var m = n / 1000000;
      return (Number.isInteger(m) ? m : Math.round(m * 10) / 10) + "M+";
    }
    if (n >= 1000) {
      var k = n / 1000;
      return (Number.isInteger(k) ? k : Math.round(k * 10) / 10) + "K+";
    }
    return Math.round(n) + "+";
  }

  function formatByKind(n, kind) {
    if (kind === "decimal") return n.toFixed(1);
    if (kind === "exact") return String(Math.round(n));
    return formatApproxCount(n);
  }

  /* ---------------- impact stats (large, animated count-up) ---------------- */
  function buildImpactStat(stat) {
    var item = document.createElement("div");
    item.className = "impact-stat";
    var icon = document.createElement("div"); icon.className = "impact-icon"; icon.textContent = stat.icon; icon.setAttribute("aria-hidden", "true");
    var value = document.createElement("div"); value.className = "impact-value";
    value.textContent = stat.display;
    if (stat.numericTarget != null) {
      value.setAttribute("data-target", String(stat.numericTarget));
      value.setAttribute("data-format", stat.format);
    }
    var label = document.createElement("div"); label.className = "impact-label"; label.textContent = stat.label;
    item.appendChild(icon); item.appendChild(value); item.appendChild(label);
    if (stat.tag) {
      var tag = document.createElement("div"); tag.className = "impact-tag"; tag.textContent = stat.tag;
      item.appendChild(tag);
    }
    return item;
  }

  var impactEl = document.getElementById("impactStats");
  if (impactEl) {
    var avg = computeAverageRating(CONFIG.reviews);
    var s = CONFIG.impactStats;
    var stats = [
      {
        icon: s.parentsInspired.icon, label: s.parentsInspired.label,
        display: formatApproxCount(s.parentsInspired.value), numericTarget: s.parentsInspired.value, format: "approx",
        tag: s.parentsInspired.demo ? "Demo data" : null
      },
      {
        icon: s.familiesReached.icon, label: s.familiesReached.label,
        display: formatApproxCount(s.familiesReached.value), numericTarget: s.familiesReached.value, format: "approx",
        tag: s.familiesReached.demo ? "Demo data" : null
      },
      avg
        ? { icon: "⭐", label: "Average Reader Rating", display: avg.toFixed(1), numericTarget: avg, format: "decimal", tag: null }
        : { icon: "⭐", label: "Average Reader Rating", display: "—", numericTarget: null, tag: "New release" },
      {
        icon: s.chaptersInside.icon, label: s.chaptersInside.label,
        display: String(s.chaptersInside.value), numericTarget: s.chaptersInside.value, format: "exact",
        tag: null
      }
    ];
    stats.forEach(function (st) { impactEl.appendChild(buildImpactStat(st)); });
  }

  // Rect-based scroll trigger (not IntersectionObserver — this repo's
  // reveal-on-scroll system already found IO unreliable in some embedded
  // webviews; matching that pattern here for the same reason).
  var statsAnimated = false;
  function maybeAnimateStats() {
    if (statsAnimated || !impactEl) return;
    var vh = window.innerHeight || document.documentElement.clientHeight;
    if (impactEl.getBoundingClientRect().top > vh * 0.85) return;
    statsAnimated = true;
    window.removeEventListener("scroll", maybeAnimateStats);
    window.removeEventListener("resize", maybeAnimateStats);

    var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    var counters = impactEl.querySelectorAll(".impact-value[data-target]");
    counters.forEach(function (el) {
      var target = parseFloat(el.getAttribute("data-target"));
      var kind = el.getAttribute("data-format");
      if (reduce || !isFinite(target)) { el.textContent = formatByKind(target, kind); return; }
      var duration = 1100;
      var start = null;
      function step(ts) {
        if (start === null) start = ts;
        var progress = Math.min(1, (ts - start) / duration);
        var eased = 1 - Math.pow(1 - progress, 3);
        el.textContent = formatByKind(target * eased, kind);
        if (progress < 1) requestAnimationFrame(step);
        else el.textContent = formatByKind(target, kind);
      }
      requestAnimationFrame(step);
    });
  }
  if (impactEl) {
    maybeAnimateStats();
    window.addEventListener("scroll", maybeAnimateStats, { passive: true });
    window.addEventListener("resize", maybeAnimateStats, { passive: true });
  }

  /* ---------------- trust badges ---------------- */
  var trustEl = document.getElementById("trustBadges");
  if (trustEl) {
    CONFIG.trustBadges.forEach(function (b) {
      var el = document.createElement("div"); el.className = "trust-badge";
      var icon = document.createElement("span"); icon.className = "trust-badge-icon"; icon.textContent = b.icon; icon.setAttribute("aria-hidden", "true");
      var text = document.createElement("span"); text.className = "trust-badge-text"; text.textContent = b.text;
      el.appendChild(icon); el.appendChild(text);
      trustEl.appendChild(el);
    });
  }

  /* ---------------- engagement pills ---------------- */
  function buildPill(id, icon, text, isButton) {
    var el = document.createElement(isButton ? "button" : "span");
    if (isButton) el.type = "button";
    el.className = "engagement-pill";
    el.id = id;
    var iconEl = document.createElement("span"); iconEl.className = "pill-icon"; iconEl.textContent = icon; iconEl.setAttribute("aria-hidden", "true");
    var textEl = document.createElement("span"); textEl.className = "pill-text"; textEl.textContent = text;
    el.appendChild(iconEl); el.appendChild(textEl);
    return el;
  }

  var pillsEl = document.getElementById("engagementPills");
  var favPill, favIcon, favText, savePill, saveIcon, saveText;
  if (pillsEl) {
    favPill = buildPill("pillFavourite", "🤍", "Add to favourites", true);
    savePill = buildPill("pillSave", "📚", "Save for later", true);
    var explorePill = buildPill("pillExplore", CONFIG.engagement.exploring.icon, CONFIG.engagement.exploring.text, false);
    var recommendPill = buildPill("pillRecommend", CONFIG.engagement.recommended.icon, CONFIG.engagement.recommended.text, false);

    pillsEl.appendChild(favPill);
    pillsEl.appendChild(savePill);
    pillsEl.appendChild(explorePill);
    pillsEl.appendChild(recommendPill);

    favIcon = favPill.querySelector(".pill-icon");
    favText = favPill.querySelector(".pill-text");
    saveIcon = savePill.querySelector(".pill-icon");
    saveText = savePill.querySelector(".pill-text");

    // Real reviews upgrade the generic "Recommended parenting resource" pill
    // with an honest computed percentage — never a fabricated one.
    if (CONFIG.reviews.length) {
      var pct = Math.round(CONFIG.reviews.filter(function (r) { return r.rating >= 4; }).length / CONFIG.reviews.length * 100);
      recommendPill.querySelector(".pill-text").textContent = pct + "% of readers recommend this book";
    }
  }

  /* ---------------- favourite (real, per-visitor, no fake counts) ---------------- */
  var LIKE_KEY = "mc_favourited";
  var likeBtn = document.getElementById("bookLike");

  function setLiked(liked) {
    if (likeBtn) {
      likeBtn.classList.toggle("is-liked", liked);
      likeBtn.setAttribute("aria-pressed", liked ? "true" : "false");
      likeBtn.setAttribute("aria-label", liked ? "Remove from favourites" : "Save The Mother's Code to your favourites");
    }
    if (favPill) favPill.classList.toggle("is-active", liked);
    if (favIcon) favIcon.textContent = liked ? "❤️" : "🤍";
    if (favText) favText.textContent = liked ? "Added to favourites" : "Add to favourites";
    try { localStorage.setItem(LIKE_KEY, liked ? "1" : "0"); } catch (e) { /* private browsing, etc. */ }
  }

  var storedLiked = false;
  try { storedLiked = localStorage.getItem(LIKE_KEY) === "1"; } catch (e) { /* private browsing, etc. */ }
  setLiked(storedLiked);

  if (likeBtn) {
    likeBtn.addEventListener("click", function () {
      setLiked(!likeBtn.classList.contains("is-liked"));
      likeBtn.classList.add("pulse");
      setTimeout(function () { likeBtn.classList.remove("pulse"); }, 420);
    });
  }
  if (favPill) {
    favPill.addEventListener("click", function () { setLiked(!favPill.classList.contains("is-active")); });
  }

  /* ---------------- save for later (real, per-visitor, no fake counts) ---------------- */
  var SAVE_KEY = "mc_saved_for_later";
  function setSaved(saved) {
    if (saveIcon) saveIcon.textContent = saved ? "✅" : "📚";
    if (saveText) saveText.textContent = saved ? "Saved for later" : "Save for later";
    if (savePill) savePill.classList.toggle("is-active", saved);
    try { localStorage.setItem(SAVE_KEY, saved ? "1" : "0"); } catch (e) { /* private browsing, etc. */ }
  }
  var storedSaved = false;
  try { storedSaved = localStorage.getItem(SAVE_KEY) === "1"; } catch (e) { /* private browsing, etc. */ }
  setSaved(storedSaved);
  if (savePill) {
    savePill.addEventListener("click", function () { setSaved(!savePill.classList.contains("is-active")); });
  }

  /* ---------------- rating summary + breakdown (real data only) ---------------- */
  function renderRatingSummary(reviews) {
    var el = document.getElementById("ratingSummary");
    if (!el) return;
    var avgReal = computeAverageRating(reviews);
    var counts = [0, 0, 0, 0, 0]; // counts[0] = 5-star .. counts[4] = 1-star

    reviews.forEach(function (r) {
      var idx = 5 - Math.max(1, Math.min(5, Math.round(r.rating)));
      counts[idx]++;
    });

    var left = document.createElement("div"); left.className = "rating-summary-left";
    var bigNum = document.createElement("div"); bigNum.className = "rating-summary-avg"; bigNum.textContent = avgReal.toFixed(1);
    var stars = document.createElement("div"); stars.className = "rating-summary-stars"; stars.textContent = starString(avgReal);
    var count = document.createElement("div"); count.className = "rating-summary-count";
    count.textContent = reviews.length + (reviews.length === 1 ? " review" : " reviews");
    left.appendChild(bigNum); left.appendChild(stars); left.appendChild(count);

    var right = document.createElement("div"); right.className = "rating-summary-bars";
    for (var star = 5; star >= 1; star--) {
      var n = counts[5 - star];
      var pct = Math.round((n / reviews.length) * 100);
      var row = document.createElement("div"); row.className = "rating-bar-row";
      var lbl = document.createElement("span"); lbl.className = "rating-bar-label"; lbl.textContent = star + "★";
      var track = document.createElement("span"); track.className = "rating-bar-track";
      var fill = document.createElement("span"); fill.className = "rating-bar-fill"; fill.style.width = pct + "%";
      track.appendChild(fill);
      var num = document.createElement("span"); num.className = "rating-bar-num"; num.textContent = n;
      row.appendChild(lbl); row.appendChild(track); row.appendChild(num);
      right.appendChild(row);
    }
    el.appendChild(left); el.appendChild(right);
  }

  /* ---------------- review cards (real data only) ---------------- */
  function buildReviewCard(r, i) {
    var card = document.createElement("article"); card.className = "review-card";

    var head = document.createElement("div"); head.className = "review-head";
    var avatar = document.createElement("div"); avatar.className = "review-avatar";
    avatar.textContent = r.initials || (r.name ? r.name.charAt(0) : "?");
    avatar.setAttribute("aria-hidden", "true");
    var meta = document.createElement("div"); meta.className = "review-meta";
    var name = document.createElement("div"); name.className = "review-name"; name.textContent = r.name || "Reader";
    var sub = document.createElement("div"); sub.className = "review-sub";
    var starsEl = document.createElement("span"); starsEl.className = "review-stars"; starsEl.textContent = starString(r.rating);
    starsEl.setAttribute("aria-label", r.rating + " out of 5 stars");
    var date = document.createElement("span"); date.className = "review-date"; date.textContent = r.date ? formatDate(r.date) : "";
    sub.appendChild(starsEl); sub.appendChild(date);
    meta.appendChild(name); meta.appendChild(sub);
    head.appendChild(avatar); head.appendChild(meta);

    var text = document.createElement("p"); text.className = "review-text"; text.textContent = r.text || "";

    var actions = document.createElement("div"); actions.className = "review-actions";
    var helpfulCount = r.helpful || 0;
    var helpfulBtn = document.createElement("button");
    helpfulBtn.type = "button"; helpfulBtn.className = "review-action";
    helpfulBtn.textContent = "Helpful (" + helpfulCount + ")";
    helpfulBtn.addEventListener("click", function () {
      helpfulCount++;
      helpfulBtn.textContent = "Helpful (" + helpfulCount + ")";
      helpfulBtn.disabled = true;
    });

    var likeKey = "mc_review_like_" + i;
    var liked = false;
    try { liked = localStorage.getItem(likeKey) === "1"; } catch (e) { /* private browsing, etc. */ }
    var heartBtn = document.createElement("button");
    heartBtn.type = "button";
    heartBtn.className = "review-action review-heart" + (liked ? " is-liked" : "");
    heartBtn.setAttribute("aria-pressed", liked ? "true" : "false");
    heartBtn.setAttribute("aria-label", "Like this review");
    heartBtn.textContent = liked ? "❤" : "🤍";
    heartBtn.addEventListener("click", function () {
      var now = !heartBtn.classList.contains("is-liked");
      heartBtn.classList.toggle("is-liked", now);
      heartBtn.setAttribute("aria-pressed", now ? "true" : "false");
      heartBtn.textContent = now ? "❤" : "🤍";
      try { localStorage.setItem(likeKey, now ? "1" : "0"); } catch (e) { /* private browsing, etc. */ }
    });

    actions.appendChild(helpfulBtn); actions.appendChild(heartBtn);

    card.appendChild(head); card.appendChild(text); card.appendChild(actions);
    return card;
  }

  if (CONFIG.reviews.length) {
    var reviewsSection = document.getElementById("reviews");
    if (reviewsSection) reviewsSection.hidden = false;

    renderRatingSummary(CONFIG.reviews);

    var listEl = document.getElementById("reviewList");
    if (listEl) CONFIG.reviews.forEach(function (r, i) { listEl.appendChild(buildReviewCard(r, i)); });
  }
})();
