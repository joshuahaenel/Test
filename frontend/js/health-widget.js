import { api } from "./app.js";

async function refreshHealth() {
  const body = document.querySelector("#health-widget .widget-body");
  try {
    const data = await api("/api/health/latest");
    if (!data.metrics || data.metrics.length === 0) {
      body.innerHTML = `<span class="empty-state">Warte auf ersten Health-Auto-Export-Sync...</span>`;
      return;
    }
    body.innerHTML = `
      <table class="mini">
        ${data.metrics
          .map((m) => `<tr><td>${m.metric}</td><td>${m.value} ${m.unit || ""}</td></tr>`)
          .join("")}
      </table>
      <p class="hint">Zuletzt synchronisiert: ${data.metrics[0].received_at}</p>
    `;
  } catch (err) {
    body.innerHTML = `<span class="error-state">${err.message}</span>`;
  }
}

export function initHealthWidget() {
  refreshHealth();
  setInterval(refreshHealth, 5 * 60_000);
}
