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

  function filter() {
    var query = normalize(input.value.trim());
    var exactTag = knownTags.hasOwnProperty(query);
    var visible = 0;
    cards.forEach(function (card) {
      var matches;
      if (!query) {
        matches = true;
      } else if (exactTag) {
        matches = (card.dataset.tags || "").split("|").indexOf(query) !== -1;
      } else {
        matches = card.dataset.search.indexOf(query) !== -1;
      }
      card.style.display = matches ? "" : "none";
      if (matches) {
        visible += 1;
      }
    });
    if (counter) {
      counter.textContent = visible + " de " + cards.length + " recetas";
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
