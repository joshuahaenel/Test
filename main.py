#!/usr/bin/env python3
"""Entry point for Jarvis.

Usage:
    python3 main.py            # text mode (type commands, works everywhere)
    python3 main.py --voice    # voice mode (needs microphone + speakers)
"""

from __future__ import annotations

import argparse
import sys

from jarvis.assistant import Jarvis


def run_text_mode(jarvis: Jarvis) -> None:
    print(jarvis.process("hallo"))
    print("(Tippe 'exit' zum Beenden.)")
    while True:
        try:
            text = input("> ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        response = jarvis.process(text)
        print(response)
        if jarvis.is_exit(text):
            break


def run_voice_mode(jarvis: Jarvis) -> None:
    from jarvis.speech import SpeechEngine, SpeechUnavailableError

    engine = SpeechEngine()
    try:
        engine.speak(jarvis.process("hallo"))
    except SpeechUnavailableError as exc:
        print(f"Sprachmodus nicht verfügbar: {exc}", file=sys.stderr)
        sys.exit(1)

    while True:
        try:
            text = engine.listen()
        except Exception as exc:  # microphone errors, unclear speech, etc.
            print(f"Ich habe dich nicht verstanden ({exc}).")
            continue
        print(f"Du: {text}")
        response = jarvis.process(text)
        print(f"Jarvis: {response}")
        engine.speak(response)
        if jarvis.is_exit(text):
            break


def main() -> None:
    parser = argparse.ArgumentParser(description="Jarvis assistant")
    parser.add_argument(
        "--voice", action="store_true", help="Sprachmodus statt Textmodus verwenden"
    )
    args = parser.parse_args()

    jarvis = Jarvis()
    if args.voice:
        run_voice_mode(jarvis)
    else:
        run_text_mode(jarvis)


if __name__ == "__main__":
    main()
