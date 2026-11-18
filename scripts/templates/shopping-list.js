// Persists checked items of the weekly shopping list in this browser,
// scoped per plan (data-plan) so different weeks don't share state.
(function () {
  "use strict";

  var list = document.querySelector(".shopping-list");
  if (!list) {
    return;
  }
  var storageKey = "recetario-compra-" + (list.getAttribute("data-plan") || "default");

  function readState() {
    try {
      var raw = window.localStorage.getItem(storageKey);
      return raw ? JSON.parse(raw) : {};
    } catch (e) {
      return {};
    }
  }

  function writeState(state) {
    try {
      window.localStorage.setItem(storageKey, JSON.stringify(state));
    } catch (e) {
      // Private browsing or storage disabled: checks just won't persist.
    }
  }

  var state = readState();
  var checkboxes = Array.prototype.slice.call(list.querySelectorAll(".shopping-check"));

  checkboxes.forEach(function (checkbox) {
    var index = checkbox.getAttribute("data-index");
    if (state[index]) {
      checkbox.checked = true;
    }
    checkbox.addEventListener("change", function () {
      state[index] = checkbox.checked;
      writeState(state);
    });
  });
})();
