import { api } from "./app.js";

export async function refreshWeather() {
  const body = document.querySelector("#weather-widget .widget-body");
  try {
    const location = localStorage.getItem("jarvis_location");
    const query = location ? `?location=${encodeURIComponent(location)}` : "";
    const data = await api(`/api/weather${query}`);
    body.innerHTML = `
      <strong>${data.location}</strong>: ${Math.round(data.temperature)}°, ${data.condition}
      <table class="mini">
        ${data.forecast
          .map(
            (day) =>
              `<tr><td>${day.date}</td><td>${Math.round(day.temperature_min)}°/${Math.round(day.temperature_max)}°</td><td>${day.condition}</td></tr>`
          )
          .join("")}
      </table>
    `;
  } catch (err) {
    body.innerHTML = `<span class="error-state">${err.message}</span>`;
  }
}

export function initWeatherWidget() {
  refreshWeather();
}
