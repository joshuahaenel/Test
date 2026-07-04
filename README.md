# Jarvis

Zwei Dinge leben in diesem Repo:

1. **Legacy-CLI** (`jarvis/`, `main.py`) — ein kleiner Text-/Sprachassistent mit
   festen Befehlen (Uhrzeit, Datum, Witz, Websuche). Läuft ohne Abhängigkeiten.
2. **Jarvis Desktop-App** (`backend/`, `frontend/`, `electron/`) — eine
   Electron-App mit echtem KI-Chat (Anthropic Claude), Dashboard, Wetter,
   Apple-Health-Anbindung, Bildschirmzeit, Trainingsplan, TimeTree-Kalender
   und der Möglichkeit, Webseiten/YouTube-Videos zu öffnen.

## Legacy-CLI

```bash
# Textmodus (Tastatur, funktioniert überall, keine Abhängigkeiten)
python3 main.py

# Sprachmodus (braucht Mikrofon/Lautsprecher + zusätzliche Pakete)
pip install -r requirements.txt
python3 main.py --voice
```

Unterstützte Befehle: Begrüßung ("hallo"), Uhrzeit ("wie spät ist es"), Datum
("welches datum haben wir"), Witz ("erzähl mir einen witz"), Websuche ("suche
nach ..."), Beenden ("exit"/"quit").

```bash
python3 -m pytest tests/
```

## Jarvis Desktop-App

### Architektur

Eine Electron-Shell startet ein lokales Python/FastAPI-Backend als Subprozess
und zeigt dessen Dashboard in einem Fenster an. Der Chat läuft über die
Anthropic-API mit Tool-Use — Jarvis kann selbst entscheiden, wann es Wetter
abfragt, eine Webseite öffnet, ein YouTube-Video abspielt, den Kalender liest
usw.

```
backend/    FastAPI-App, Claude-Tool-Use, SQLite-Speicher für Health/
            Bildschirmzeit/Trainingsplan, TimeTree-ICS-Client
frontend/   Statisches Dashboard (Chat, Widgets), vom Backend ausgeliefert
electron/   Electron-Shell, die das Backend startet und das Dashboard anzeigt
```

### Einrichtung

1. **Backend-Abhängigkeiten installieren:**
   ```bash
   pip install -r backend/requirements.txt
   ```

2. **Konfiguration anlegen:**
   ```bash
   cp backend/.env.example backend/.env
   ```
   Trage in `backend/.env` ein:
   - `ANTHROPIC_API_KEY` — von [console.anthropic.com](https://console.anthropic.com)
   - `HEALTH_WEBHOOK_SECRET` — ein selbst gewähltes, langes Zufalls-Secret
   - `TIMETREE_ICS_URL` — der Freigabelink (ICS/Webcal) aus TimeTree
     ("Kalender teilen" → Link erzeugen). TimeTree hat seit 2020 keine
     öffentliche API mehr; dieser read-only Feed-Link ist der einzig
     stabile Weg, Termine zu lesen (keine Termin-Erstellung möglich).

3. **Nur das Backend testen (im Browser, ohne Electron):**
   ```bash
   python3 -m uvicorn backend.app:app --reload
   ```
   Dashboard dann unter http://localhost:8000 öffnen.

4. **Als Desktop-App über Electron starten:**
   ```bash
   cd electron
   npm install
   npm start
   ```
   Electron startet das Backend automatisch als Subprozess und öffnet das
   Dashboard-Fenster.

### Apple Health anbinden

Apple erlaubt keinen direkten Server-Zugriff auf HealthKit-Daten. Stattdessen:
installiere die App **Health Auto Export** (oder baue eine iOS-Kurzbefehl-
Automation) auf dem iPhone und richte sie so ein, dass sie periodisch einen
`POST` an `http://<Rechner-IP>:8000/api/health/webhook` mit Header
`X-Webhook-Token: <HEALTH_WEBHOOK_SECRET>` sendet.

**Wichtig:** iPhone und Rechner müssen sich erreichen können — im selben WLAN
funktioniert das über die lokale IP. Für Zugriff außerhalb des Heimnetzes wird
[Tailscale](https://tailscale.com) empfohlen (privates Mesh-VPN); bei ngrok
oder ähnlichem ist der Token-Check sicherheitskritisch, da der Endpunkt dann
öffentlich erreichbar ist.

### Bildschirmzeit & Trainingsplan

Beides läuft komplett lokal, ohne externe Dienste:
- **Bildschirmzeit**: Apple bietet keine Export-API/Kurzbefehl-Aktion dafür,
  daher trägst du den Wert manuell im Dashboard-Widget ein (oder sagst Jarvis
  im Chat z.B. "heute hatte ich 3 Stunden 20 Bildschirmzeit").
- **Trainingsplan**: direkt im Dashboard-Widget pro Wochentag bearbeitbar.

### Tests

```bash
python3 -m pytest tests/ backend/tests/
```

Headless testbar (keine echten Keys/Hardware nötig): Wetter-Parsing, alle
Claude-Tools einzeln, Health-/Bildschirmzeit-/Trainingsplan-Storage,
Webhook-Auth, Kalender-Parsing, der komplette Chat-Tool-Use-Loop (gemockter
Anthropic-Client), sowie die 10 Legacy-CLI-Tests.

Nur manuell auf dem eigenen Rechner verifizierbar: Sprache (echtes Mikrofon/
Lautsprecher), das Electron-Fenster, echte Health-Auto-Export-Payloads, echte
LAN/Tunnel-Erreichbarkeit, und ein Live-Smoke-Test gegen die echte
Anthropic-API.

## Erweitern

Ein neues Claude-Tool hinzufügen: Funktion in einer passenden Datei unter
`backend/tools/` ergänzen, Schema + Dispatch-Eintrag in
`backend/tools/registry.py` eintragen. Für die Legacy-CLI: Handler-Funktion in
`jarvis/commands.py` ergänzen und Erkennung in `jarvis/assistant.py`
eintragen.
