/* The Mother's Code — social proof: stats, reviews, favourites.
   Single config below. Nothing here is hardcoded elsewhere in the page —
   edit CONFIG (or swap the `reviews` array for a real API call) and every
   card/badge/section updates itself, including hiding/showing automatically.

   Honesty rules baked into this file, on purpose:
   - Numbers marked `demo: true` render with a visible "Demo data" tag until
     you replace them with real figures.
   - Average rating, the star breakdown, the recommend %, and the whole
     Reviews section are NEVER faked — they're computed from `reviews` and
     stay hidden until that array actually has real entries in it. */
(function () {
  "use strict";

  var CONFIG = {
    stats: {
      copiesDelivered: { icon: "📖", label: "Copies Delivered", value: "1,000+", demo: true },
      chaptersInside:  { icon: "📚", label: "Chapters Inside",  value: "21",     demo: false },
      readersHelped:   { icon: "💛", label: "Readers Helped",   value: "800+",  demo: true }
    },
    engagement: {
      viewedToday: { value: 142, demo: true }
    },
    // Add real reviews as they come in. Shape:
    // { name: "J.", initials: "J", rating: 5, date: "2026-06-02", text: "...", helpful: 0 }
    // The rating summary, star breakdown, recommend %, and Reviews section
    // all activate automatically the moment this array is non-empty.
    reviews: []
  };

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

  /* ---------------- stat cards ---------------- */
  function buildStatCard(c) {
    var card = document.createElement("div");
    card.className = "stat-card";
    var icon = document.createElement("div"); icon.className = "stat-icon"; icon.textContent = c.icon; icon.setAttribute("aria-hidden", "true");
    var value = document.createElement("div"); value.className = "stat-value"; value.textContent = c.value;
    var label = document.createElement("div"); label.className = "stat-label"; label.textContent = c.label;
    card.appendChild(icon); card.appendChild(value); card.appendChild(label);
    var tagText = c.demo ? "Demo data" : c.note;
    if (tagText) {
      var tag = document.createElement("div"); tag.className = "stat-demo-tag"; tag.textContent = tagText;
      card.appendChild(tag);
    }
    return card;
  }

  var statsEl = document.getElementById("spStats");
  if (statsEl) {
    var avgForStats = computeAverageRating(CONFIG.reviews);
    var ratingCard = avgForStats
      ? { icon: "⭐", label: "Average Rating", value: avgForStats.toFixed(1), demo: false }
      : { icon: "⭐", label: "Average Rating", value: "—", demo: false, note: "New release" };
    [CONFIG.stats.copiesDelivered, ratingCard, CONFIG.stats.chaptersInside, CONFIG.stats.readersHelped]
      .forEach(function (c) { statsEl.appendChild(buildStatCard(c)); });
  }

  /* ---------------- "viewed today" demo badge ---------------- */
  var viewedBadge = document.querySelector("#spViewedBadge .sp-badge-text");
  if (viewedBadge) {
    viewedBadge.textContent = CONFIG.engagement.viewedToday.value + " parents viewed today"
      + (CONFIG.engagement.viewedToday.demo ? " (demo)" : "");
  }

  /* ---------------- favourite / like button (real — reflects this visitor's own choice, no fake counts) ---------------- */
  var LIKE_KEY = "mc_favourited";
  var likeBtn = document.getElementById("bookLike");
  var favBadgeText = document.querySelector("#spFavBadge .sp-badge-text");
  var favBadgeIcon = document.querySelector("#spFavBadge .sp-badge-icon");

  function setLiked(liked) {
    if (likeBtn) {
      likeBtn.classList.toggle("is-liked", liked);
      likeBtn.setAttribute("aria-pressed", liked ? "true" : "false");
      likeBtn.setAttribute("aria-label", liked ? "Remove from favourites" : "Save The Mother's Code to your favourites");
    }
    if (favBadgeText) favBadgeText.textContent = liked ? "Added to your favourites" : "Add it to your favourites";
    if (favBadgeIcon) favBadgeIcon.textContent = liked ? "❤️" : "🤍";
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

  /* ---------------- rating summary + breakdown (real data only) ---------------- */
  function renderRatingSummary(reviews) {
    var el = document.getElementById("ratingSummary");
    if (!el) return;
    var avg = computeAverageRating(reviews);
    var counts = [0, 0, 0, 0, 0]; // counts[0] = 5-star .. counts[4] = 1-star

    reviews.forEach(function (r) {
      var idx = 5 - Math.max(1, Math.min(5, Math.round(r.rating)));
      counts[idx]++;
    });

    var left = document.createElement("div"); left.className = "rating-summary-left";
    var bigNum = document.createElement("div"); bigNum.className = "rating-summary-avg"; bigNum.textContent = avg.toFixed(1);
    var stars = document.createElement("div"); stars.className = "rating-summary-stars"; stars.textContent = starString(avg);
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

    var recBadge = document.getElementById("spRecommendBadge");
    if (recBadge) {
      var recommendPct = Math.round(
        CONFIG.reviews.filter(function (r) { return r.rating >= 4; }).length / CONFIG.reviews.length * 100
      );
      recBadge.hidden = false;
      recBadge.querySelector(".sp-badge-text").textContent = recommendPct + "% of readers recommend this book";
    }
  }
})();
