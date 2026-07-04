import { api } from "./app.js";

async function saveDay(day, textarea) {
  await api("/api/training-plan", {
    method: "PUT",
    body: JSON.stringify({ day, description: textarea.value }),
  });
}

async function refreshTrainingPlan() {
  const body = document.querySelector("#training-widget .widget-body");
  try {
    const plan = await api("/api/training-plan");
    body.innerHTML = Object.entries(plan)
      .map(
        ([day, description]) => `
          <div class="training-day">
            <label>${day}</label>
            <textarea data-day="${day}">${description}</textarea>
          </div>
        `
      )
      .join("");

    body.querySelectorAll("textarea").forEach((textarea) => {
      textarea.addEventListener("blur", () => saveDay(textarea.dataset.day, textarea));
    });
  } catch (err) {
    body.innerHTML = `<span class="error-state">${err.message}</span>`;
  }
}

export function initTrainingWidget() {
  refreshTrainingPlan();
}
