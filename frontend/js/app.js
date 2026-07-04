import { initChat, sendMessageFromVoice } from "./chat.js";
import { initWeatherWidget, refreshWeather } from "./weather-widget.js";
import { initHealthWidget } from "./health-widget.js";
import { initScreenTimeWidget } from "./screen-time-widget.js";
import { initTrainingWidget } from "./training-widget.js";
import { initCalendarWidget } from "./calendar-widget.js";
import { initSettingsWidget } from "./settings.js";
import { initVoice } from "./voice.js";

const SESSION_KEY = "jarvis_session_id";

export function getSessionId() {
  let sessionId = localStorage.getItem(SESSION_KEY);
  if (!sessionId) {
    sessionId = crypto.randomUUID();
    localStorage.setItem(SESSION_KEY, sessionId);
  }
  return sessionId;
}

export async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed: ${response.status}`);
  }
  if (response.status === 204) return null;
  return response.json();
}

function updateClock() {
  const el = document.getElementById("clock");
  el.textContent = new Date().toLocaleTimeString("de-DE", {
    hour: "2-digit",
    minute: "2-digit",
  });
}

async function checkConnection() {
  const dot = document.getElementById("connection-dot");
  try {
    await fetch("/healthz");
    dot.classList.add("online");
  } catch {
    dot.classList.remove("online");
  }
}

function bootstrap() {
  updateClock();
  setInterval(updateClock, 30_000);
  checkConnection();
  setInterval(checkConnection, 15_000);

  initChat();
  initVoice(sendMessageFromVoice);
  initSettingsWidget();
  initWeatherWidget();
  initHealthWidget();
  initScreenTimeWidget();
  initTrainingWidget();
  initCalendarWidget();

  setInterval(refreshWeather, 10 * 60_000);
}

document.addEventListener("DOMContentLoaded", bootstrap);
