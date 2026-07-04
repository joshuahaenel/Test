import { api, getSessionId } from "./app.js";
import { speak, isAutoSpeakEnabled } from "./voice.js";
import { playYoutubeVideo } from "./youtube-widget.js";

function appendMessage(text, role) {
  const messages = document.getElementById("messages");
  const bubble = document.createElement("div");
  bubble.className = `message ${role}`;
  bubble.textContent = text;
  messages.appendChild(bubble);
  messages.scrollTop = messages.scrollHeight;
}

function applyActions(actions) {
  for (const action of actions || []) {
    if (action.type === "play_youtube") {
      playYoutubeVideo(action.embed_url);
    }
  }
}

async function sendMessage(text) {
  appendMessage(text, "user");
  try {
    const response = await api("/api/chat", {
      method: "POST",
      body: JSON.stringify({ session_id: getSessionId(), message: text }),
    });
    appendMessage(response.reply, "assistant");
    applyActions(response.actions);
    if (isAutoSpeakEnabled()) speak(response.reply);
  } catch (err) {
    appendMessage(`Fehler: ${err.message}`, "system");
  }
}

export function sendMessageFromVoice(text) {
  sendMessage(text);
}

export function initChat() {
  const form = document.getElementById("composer");
  const input = document.getElementById("message-input");

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const text = input.value.trim();
    if (!text) return;
    input.value = "";
    sendMessage(text);
  });

  appendMessage("Hallo, ich bin Jarvis. Wie kann ich helfen?", "assistant");
}
