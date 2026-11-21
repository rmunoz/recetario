// Client-side search for the recipe list. Filters the cards that are
// already in the HTML; no backend, no data fetch needed.
(function () {
  "use strict";

  function normalize(s) {
    return s
      .toLowerCase()
      .normalize("NFD")
      .replace(/[̀-ͯ]/g, "");
  }

  var input = document.getElementById("search");
  var counter = document.getElementById("counter");
  var cards = Array.prototype.slice.call(document.querySelectorAll(".card"));
  if (!input || !cards.length) {
    return;
  }

  // Tags are plain lowercase/no-accent strings (repo convention), so an
  // exact match against a known tag switches to exact filtering instead
  // of the usual substring search — "col" shouldn't also match "coliflor".
  var knownTags = {};
  cards.forEach(function (card) {
    (card.dataset.tags || "").split("|").forEach(function (t) {
      if (t) {
        knownTags[t] = true;
      }
    });
  });

  // Variants (cards with data-variant) stay out of the plain listing so a
  // recipe with many variants doesn't crowd the rest; they only appear when
  // a search or tag filter matches them.
  var mainTotal = cards.filter(function (card) {
    return !card.hasAttribute("data-variant");
  }).length;

  function filter() {
    var query = normalize(input.value.trim());
    var exactTag = knownTags.hasOwnProperty(query);
    var visibleMain = 0;
    var visibleVariants = 0;
    cards.forEach(function (card) {
      var isVariant = card.hasAttribute("data-variant");
      var matches;
      if (!query) {
        matches = !isVariant;
      } else if (exactTag) {
        matches = (card.dataset.tags || "").split("|").indexOf(query) !== -1;
      } else {
        matches = card.dataset.search.indexOf(query) !== -1;
      }
      card.hidden = !matches;
      if (matches) {
        if (isVariant) {
          visibleVariants += 1;
        } else {
          visibleMain += 1;
        }
      }
    });
    if (counter) {
      var text = visibleMain + " de " + mainTotal + " recetas";
      if (visibleVariants) {
        text += " y " + visibleVariants + (visibleVariants === 1 ? " variante" : " variantes");
      }
      counter.textContent = text;
    }
  }

  // Clicking a tag filters in place instead of reloading the page (the
  // tag's href still points at index.html?tag=... as a no-JS fallback,
  // and that's also how a recipe page's tag links land here filtered).
  document.querySelectorAll(".tag").forEach(function (tag) {
    tag.addEventListener("click", function (event) {
      event.preventDefault();
      input.value = tag.textContent.trim();
      filter();
      input.scrollIntoView({ behavior: "smooth", block: "nearest" });
    });
  });

  var presetTag = new URLSearchParams(window.location.search).get("tag");
  if (presetTag) {
    input.value = presetTag;
  }

  input.addEventListener("input", filter);
  filter();
})();
