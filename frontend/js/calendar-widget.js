import { api } from "./app.js";

function formatWhen(isoStart) {
  return new Date(isoStart).toLocaleString("de-DE", {
    weekday: "short",
    day: "2-digit",
    month: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

async function refreshCalendar() {
  const body = document.querySelector("#calendar-widget .widget-body");
  try {
    const events = await api("/api/calendar/events?days=7");
    if (events.length === 0) {
      body.innerHTML = `<span class="empty-state">Keine anstehenden Termine.</span>`;
      return;
    }
    body.innerHTML = events
      .slice(0, 5)
      .map(
        (event) => `
          <div class="calendar-event">
            <div>${event.summary}</div>
            <div class="when">${formatWhen(event.start)}${event.location ? " · " + event.location : ""}</div>
          </div>
        `
      )
      .join("");
  } catch (err) {
    body.innerHTML = `<span class="hint">${err.message}</span>`;
  }
}

export function initCalendarWidget() {
  refreshCalendar();
  setInterval(refreshCalendar, 15 * 60_000);
}
