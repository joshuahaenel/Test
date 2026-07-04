import { api } from "./app.js";
import { isAutoSpeakEnabled, setAutoSpeakEnabled } from "./voice.js";

export async function initSettingsWidget() {
  const locationInput = document.getElementById("settings-location");
  const autoSpeakInput = document.getElementById("settings-auto-speak");
  const modelHint = document.getElementById("settings-model");

  autoSpeakInput.checked = isAutoSpeakEnabled();

  try {
    const config = await api("/api/config");
    locationInput.value = config.default_location;
    modelHint.textContent = `Modell: ${config.model_name}`;
    localStorage.setItem("jarvis_location", config.default_location);
  } catch {
    modelHint.textContent = "Konfiguration konnte nicht geladen werden.";
  }

  locationInput.addEventListener("change", async () => {
    localStorage.setItem("jarvis_location", locationInput.value);
    await api("/api/config", {
      method: "POST",
      body: JSON.stringify({ default_location: locationInput.value }),
    });
  });

  autoSpeakInput.addEventListener("change", () => {
    setAutoSpeakEnabled(autoSpeakInput.checked);
  });
}
