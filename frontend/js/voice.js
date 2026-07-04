// Voice I/O via the browser-native Web Speech API. Simpler than a
// server-side STT/TTS pipeline (no PyAudio/mic-access plumbing needed) and
// runs natively in Electron's Chromium renderer.

const AUTO_SPEAK_KEY = "jarvis_auto_speak";
const SpeechRecognitionImpl = window.SpeechRecognition || window.webkitSpeechRecognition;

let recognizer = null;
let listening = false;

export function isAutoSpeakEnabled() {
  return localStorage.getItem(AUTO_SPEAK_KEY) !== "false";
}

export function setAutoSpeakEnabled(enabled) {
  localStorage.setItem(AUTO_SPEAK_KEY, String(enabled));
  updateSpeakButton();
}

function updateSpeakButton() {
  const button = document.getElementById("speak-toggle");
  if (!button) return;
  button.classList.toggle("active", isAutoSpeakEnabled());
}

export function speak(text) {
  if (!("speechSynthesis" in window) || !text) return;
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = "de-DE";
  window.speechSynthesis.speak(utterance);
}

function setMicActive(active) {
  const button = document.getElementById("mic-button");
  if (button) button.classList.toggle("active", active);
}

export function initVoice(onTranscript) {
  updateSpeakButton();

  const speakToggle = document.getElementById("speak-toggle");
  speakToggle?.addEventListener("click", () => setAutoSpeakEnabled(!isAutoSpeakEnabled()));

  const micButton = document.getElementById("mic-button");
  if (!SpeechRecognitionImpl) {
    if (micButton) {
      micButton.disabled = true;
      micButton.title = "Spracherkennung wird von diesem Browser nicht unterstützt.";
    }
    return;
  }

  recognizer = new SpeechRecognitionImpl();
  recognizer.lang = "de-DE";
  recognizer.interimResults = false;
  recognizer.maxAlternatives = 1;

  recognizer.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    onTranscript(transcript);
  };
  recognizer.onend = () => {
    listening = false;
    setMicActive(false);
  };
  recognizer.onerror = () => {
    listening = false;
    setMicActive(false);
  };

  micButton?.addEventListener("click", () => {
    if (listening) {
      recognizer.stop();
      return;
    }
    listening = true;
    setMicActive(true);
    recognizer.start();
  });
}
