// Quick year/month filter for the weekly-plan history page. Filters the
// week cards already in the HTML; no backend, no data fetch needed.
(function () {
  "use strict";

  var grid = document.getElementById("plan-grid");
  var counter = document.getElementById("plan-counter");
  if (!grid) {
    return;
  }
  var cards = Array.prototype.slice.call(grid.querySelectorAll(".week-card"));
  var yearGroup = document.getElementById("year-filters");
  var monthGroup = document.getElementById("month-filters");

  function activeValue(group, attr) {
    if (!group) {
      return "";
    }
    var active = group.querySelector(".chip.active");
    return active ? active.getAttribute(attr) : "";
  }

  function filter() {
    var year = activeValue(yearGroup, "data-filter-year");
    var month = activeValue(monthGroup, "data-filter-month");
    var visible = 0;
    cards.forEach(function (card) {
      var matches = (!year || card.dataset.year === year) && (!month || card.dataset.month === month);
      card.style.display = matches ? "" : "none";
      if (matches) {
        visible += 1;
      }
    });
    if (counter) {
      counter.textContent = visible + " de " + cards.length + " semanas";
    }
  }

  function wireGroup(group) {
    if (!group) {
      return;
    }
    Array.prototype.slice.call(group.querySelectorAll(".chip")).forEach(function (chip) {
      chip.addEventListener("click", function () {
        Array.prototype.slice.call(group.querySelectorAll(".chip")).forEach(function (c) {
          c.classList.remove("active");
        });
        chip.classList.add("active");
        filter();
      });
    });
  }

  wireGroup(yearGroup);
  wireGroup(monthGroup);
  filter();
})();
