import { api } from "./app.js";

function formatMinutes(minutes) {
  const hours = Math.floor(minutes / 60);
  const rest = minutes % 60;
  return hours > 0 ? `${hours}h ${rest}min` : `${rest}min`;
}

async function refreshScreenTime() {
  const body = document.querySelector("#screen-time-widget .widget-body");
  try {
    const entries = await api("/api/screen-time?days=7");
    if (entries.length === 0) {
      body.innerHTML = `<span class="empty-state">Noch keine Einträge.</span>`;
      return;
    }
    body.innerHTML = `
      <table class="mini">
        ${entries.map((e) => `<tr><td>${e.date}</td><td>${formatMinutes(e.minutes)}</td></tr>`).join("")}
      </table>
    `;
  } catch (err) {
    body.innerHTML = `<span class="error-state">${err.message}</span>`;
  }
}

export function initScreenTimeWidget() {
  refreshScreenTime();

  const form = document.getElementById("screen-time-form");
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const input = document.getElementById("screen-time-minutes");
    const minutes = Number(input.value);
    if (!minutes && minutes !== 0) return;
    await api("/api/screen-time", {
      method: "POST",
      body: JSON.stringify({ minutes }),
    });
    input.value = "";
    refreshScreenTime();
  });
}
