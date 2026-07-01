# Jarvis

Ein kleiner, erweiterbarer Sprachassistent in Python (inspiriert von Tony
Starks "Jarvis"). Läuft standardmäßig im Textmodus ohne zusätzliche
Abhängigkeiten; ein optionaler Sprachmodus kann per Flag aktiviert werden.

## Nutzung

```bash
# Textmodus (Tastatur, funktioniert überall)
python3 main.py

# Sprachmodus (braucht Mikrofon/Lautsprecher + zusätzliche Pakete)
pip install -r requirements.txt
python3 main.py --voice
```

## Unterstützte Befehle

- Begrüßung: "hallo", "hi"
- Uhrzeit: "wie spät ist es", "uhrzeit"
- Datum: "welches datum haben wir"
- Witz: "erzähl mir einen witz"
- Websuche: "suche nach <Begriff>"
- Beenden: "exit", "quit", "tschüss"

## Projektstruktur

```
jarvis/
  assistant.py   # Kommando-Dispatch (Text -> Antwort)
  commands.py    # Einzelne Befehlshandler (testbar, keine Seiteneffekte)
  speech.py      # Optionale STT/TTS-Anbindung (SpeechRecognition/pyttsx3)
main.py          # CLI-Einstiegspunkt (Text- und Sprachmodus)
tests/           # Unit-Tests (pytest)
```

## Tests

```bash
pip install pytest
python3 -m pytest tests/
```

## Erweitern

Neue Fähigkeiten hinzufügen: Handler-Funktion in `jarvis/commands.py`
ergänzen und passende Erkennung in `Jarvis.process()` in
`jarvis/assistant.py` eintragen.
