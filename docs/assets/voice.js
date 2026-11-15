// Voice mode for a recipe page: dictates the steps and lets you move
// through them by voice ("siguiente", "atrás", "repite", "ingredientes",
// "para") or with the always-visible fallback buttons. No frameworks, no
// dependencies, same IIFE style as search.js.
(function () {
  "use strict";

  var SpeechRecognitionImpl = window.SpeechRecognition || window.webkitSpeechRecognition;
  var speechSupported = !!SpeechRecognitionImpl && !!window.speechSynthesis;

  var stepsDataEl = document.getElementById("steps-data");
  var steps = stepsDataEl ? JSON.parse(stepsDataEl.textContent || "[]") : [];
  if (!steps.length) {
    return;
  }

  var currentStepIndex = 0;
  var state = "idle"; // idle | listening | speaking | error
  var shouldBeListening = false;
  var manualStop = false;
  var recognition = null;

  var statusEl = document.getElementById("voice-status");
  var startButton = document.getElementById("voice-start");
  var stopButton = document.getElementById("voice-stop");
  var stepNavCurrent = document.getElementById("step-nav-current");

  function normalize(text) {
    return text
      .toLowerCase()
      .normalize("NFD")
      .replace(/[̀-ͯ]/g, "")
      .replace(/[^a-z0-9\s]/g, " ")
      .trim();
  }

  // Classic dynamic-programming edit distance, used with a small threshold
  // so short recognizer typos ("siguente", "siguemos") still match their
  // canonical keyword without a hand-maintained list of every misspelling.
  function levenshtein(a, b) {
    var m = a.length;
    var n = b.length;
    var d = [];
    var i, j;
    for (i = 0; i <= m; i++) {
      d[i] = [i];
    }
    for (j = 0; j <= n; j++) {
      d[0][j] = j;
    }
    for (i = 1; i <= m; i++) {
      for (j = 1; j <= n; j++) {
        if (a.charAt(i - 1) === b.charAt(j - 1)) {
          d[i][j] = d[i - 1][j - 1];
        } else {
          d[i][j] = Math.min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + 1);
        }
      }
    }
    return d[m][n];
  }

  var COMMANDS = [
    { action: "next", keyword: "siguiente", variants: ["siguiente", "vale siguiente", "sigamos", "continua", "adelante"] },
    { action: "previous", keyword: "atras", variants: ["atras", "anterior", "paso anterior", "vuelve"] },
    { action: "repeat", keyword: "repite", variants: ["repite", "repetir", "otra vez", "como"] },
    { action: "ingredients", keyword: "ingredientes", variants: ["ingredientes", "que necesito", "lista de ingredientes"] },
    { action: "stop", keyword: "para", variants: ["para", "parar", "detener", "stop", "basta"] }
  ];

  function matchesCommand(normalizedPhrase, words, command) {
    var i, j;
    for (i = 0; i < command.variants.length; i++) {
      if (normalizedPhrase.indexOf(command.variants[i]) !== -1) {
        return true;
      }
    }
    var threshold = command.keyword.length <= 5 ? 1 : 2;
    for (j = 0; j < words.length; j++) {
      if (levenshtein(words[j], command.keyword) <= threshold) {
        return true;
      }
    }
    return false;
  }

  function procesarFrase(phrase) {
    var normalized = normalize(phrase);
    var words = normalized.split(/\s+/).filter(Boolean);
    for (var i = 0; i < COMMANDS.length; i++) {
      if (matchesCommand(normalized, words, COMMANDS[i])) {
        runCommand(COMMANDS[i].action);
        return;
      }
    }
    // Not recognized: keep listening quietly instead of interrupting
    // anything, so background noise the recognizer mistranscribes doesn't
    // derail the session.
  }

  function runCommand(action) {
    if (action === "next") {
      goToStep(currentStepIndex + 1);
    } else if (action === "previous") {
      goToStep(currentStepIndex - 1);
    } else if (action === "repeat") {
      announceCurrentStep();
    } else if (action === "ingredients") {
      speakIngredients();
    } else if (action === "stop") {
      stopVoiceMode();
    }
  }

  function showStatus(text) {
    if (statusEl) {
      statusEl.textContent = text;
    }
  }

  function highlightCurrentStep() {
    document.querySelectorAll(".steps li").forEach(function (li) {
      li.classList.remove("current-step");
    });
    var current = document.querySelector('.steps li[data-step-index="' + currentStepIndex + '"]');
    if (current) {
      current.classList.add("current-step");
      current.scrollIntoView({ behavior: "smooth", block: "center" });
    }
    if (stepNavCurrent) {
      stepNavCurrent.textContent = "Paso " + (currentStepIndex + 1) + " de " + steps.length;
    }
  }

  // Closes the mic before speaking and reopens it once speechSynthesis
  // finishes, so the browser's own voice never gets transcribed back as a
  // command.
  function speak(text, onEnd) {
    if (!window.speechSynthesis) {
      if (onEnd) {
        onEnd();
      }
      return;
    }
    stopRecognition();
    state = "speaking";
    showStatus("Leyendo el paso…");
    speechSynthesis.cancel();
    var utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "es-ES";
    utterance.onend = function () {
      if (onEnd) {
        onEnd();
      }
      if (shouldBeListening) {
        state = "listening";
        showStatus("Escuchando… di «siguiente», «atrás», «repite», «ingredientes» o «para».");
        startRecognition();
      } else {
        state = "idle";
        showStatus("");
      }
    };
    utterance.onerror = utterance.onend;
    speechSynthesis.speak(utterance);
  }

  function announceCurrentStep() {
    highlightCurrentStep();
    speak(steps[currentStepIndex]);
  }

  function goToStep(index) {
    if (index < 0) {
      speak("Este es el primer paso.");
      return;
    }
    if (index >= steps.length) {
      speak("Ya estás en el último paso.");
      return;
    }
    currentStepIndex = index;
    announceCurrentStep();
  }

  function speakIngredients() {
    var texts = Array.prototype.map.call(document.querySelectorAll(".ingredients li"), function (li) {
      var clone = li.cloneNode(true);
      var link = clone.querySelector(".ingredient-link");
      if (link) {
        link.parentNode.removeChild(link);
      }
      return clone.textContent.trim();
    });
    speak(texts.join(". "));
  }

  function createRecognition() {
    var instance = new SpeechRecognitionImpl();
    instance.lang = "es-ES";
    instance.continuous = false;
    instance.interimResults = false;
    instance.onresult = function (event) {
      var said = event.results[event.results.length - 1][0].transcript;
      procesarFrase(said);
    };
    instance.onerror = function (event) {
      handleRecognitionError(event.error);
    };
    instance.onend = function () {
      if (shouldBeListening && !manualStop) {
        startRecognition(); // cut itself off (silence/timeout); pick it back up
      }
      manualStop = false;
    };
    return instance;
  }

  function startRecognition() {
    recognition = createRecognition();
    try {
      recognition.start();
    } catch (err) {
      // Already running, or the mic refused to reopen immediately: ignore.
    }
  }

  function stopRecognition() {
    if (recognition) {
      manualStop = true;
      try {
        recognition.stop();
      } catch (err) {
        // Not running, nothing to stop.
      }
    }
  }

  function handleRecognitionError(error) {
    if (error === "not-allowed" || error === "service-not-allowed") {
      shouldBeListening = false;
      state = "error";
      showStatus("No se pudo acceder al micrófono. Usa los botones de abajo.");
      if (startButton) {
        startButton.hidden = false;
      }
      if (stopButton) {
        stopButton.hidden = true;
      }
    }
    // Other errors (e.g. "no-speech") are ignored: onend's auto-restart
    // above already takes care of continuing to listen.
  }

  function startVoiceMode() {
    shouldBeListening = true;
    if (startButton) {
      startButton.hidden = true;
    }
    if (stopButton) {
      stopButton.hidden = false;
    }
    announceCurrentStep();
  }

  function stopVoiceMode() {
    shouldBeListening = false;
    stopRecognition();
    speechSynthesis.cancel();
    state = "idle";
    showStatus("");
    if (startButton) {
      startButton.hidden = false;
    }
    if (stopButton) {
      stopButton.hidden = true;
    }
  }

  function wireVoiceButtons() {
    if (startButton) {
      startButton.addEventListener("click", startVoiceMode);
    }
    if (stopButton) {
      stopButton.addEventListener("click", stopVoiceMode);
    }
  }

  // Always wired, regardless of voice support: this is the no-voice
  // fallback. It also reads the step aloud via speechSynthesis when that's
  // available, even if the user never turned on recognition — hands-free
  // output without needing the mic.
  function wireFallbackButtons() {
    var prevButton = document.getElementById("step-prev");
    var nextButton = document.getElementById("step-next");
    if (prevButton) {
      prevButton.addEventListener("click", function () {
        goToStep(currentStepIndex - 1);
      });
    }
    if (nextButton) {
      nextButton.addEventListener("click", function () {
        goToStep(currentStepIndex + 1);
      });
    }
    highlightCurrentStep();
  }

  function init() {
    wireFallbackButtons();
    if (!speechSupported) {
      var voiceMode = document.getElementById("voice-mode");
      if (voiceMode) {
        voiceMode.hidden = true;
      }
      return;
    }
    wireVoiceButtons();
  }

  init();
})();
