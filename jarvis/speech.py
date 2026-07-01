"""Optional speech I/O for Jarvis.

Voice mode depends on `SpeechRecognition`, `pyttsx3` and a working
microphone/audio backend, none of which are guaranteed to be present
(e.g. in headless/CI environments). Imports are therefore deferred into
the class methods so that `import jarvis.speech` never fails, and a
clear error is raised only when voice mode is actually used without the
right dependencies installed.
"""

from __future__ import annotations


class SpeechUnavailableError(RuntimeError):
    pass


class SpeechEngine:
    """Thin wrapper around SpeechRecognition (STT) and pyttsx3 (TTS)."""

    def __init__(self) -> None:
        self._recognizer = None
        self._tts = None

    def _ensure_stt(self):
        if self._recognizer is None:
            try:
                import speech_recognition as sr
            except ImportError as exc:
                raise SpeechUnavailableError(
                    "Spracherkennung fehlt. Installiere sie mit: "
                    "pip install SpeechRecognition pyaudio"
                ) from exc
            self._recognizer = sr.Recognizer()
        return self._recognizer

    def _ensure_tts(self):
        if self._tts is None:
            try:
                import pyttsx3
            except ImportError as exc:
                raise SpeechUnavailableError(
                    "Sprachausgabe fehlt. Installiere sie mit: pip install pyttsx3"
                ) from exc
            self._tts = pyttsx3.init()
        return self._tts

    def listen(self) -> str:
        import speech_recognition as sr

        recognizer = self._ensure_stt()
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)
        return recognizer.recognize_google(audio, language="de-DE")

    def speak(self, text: str) -> None:
        engine = self._ensure_tts()
        engine.say(text)
        engine.runAndWait()
