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

  function filter() {
    var query = normalize(input.value.trim());
    var visible = 0;
    cards.forEach(function (card) {
      var matches = !query || card.dataset.search.indexOf(query) !== -1;
      card.style.display = matches ? "" : "none";
      if (matches) {
        visible += 1;
      }
    });
    if (counter) {
      counter.textContent = visible + " de " + cards.length + " recetas";
    }
  }

  input.addEventListener("input", filter);
  filter();
})();
