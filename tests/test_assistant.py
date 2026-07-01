import datetime

from jarvis import commands
from jarvis.assistant import Jarvis


def test_greeting():
    jarvis = Jarvis()
    assert "Jarvis" in jarvis.process("hallo")


def test_time_command():
    jarvis = Jarvis()
    response = jarvis.process("wie spät ist es")
    assert "Uhr" in response


def test_date_command():
    jarvis = Jarvis()
    response = jarvis.process("welches datum haben wir")
    assert "Heute ist der" in response


def test_joke_command():
    jarvis = Jarvis()
    response = jarvis.process("erzähl mir einen witz")
    assert response in commands.JOKES


def test_unknown_command():
    jarvis = Jarvis()
    response = jarvis.process("mach mir einen kaffee")
    assert "nicht verstanden" in response


def test_exit_detection():
    jarvis = Jarvis()
    assert jarvis.is_exit("exit")
    assert jarvis.is_exit("Quit")
    assert not jarvis.is_exit("hallo")


def test_empty_input():
    jarvis = Jarvis()
    assert jarvis.process("") == "Ich habe nichts gehört."


def test_web_search_calls_opener_with_query():
    calls = []
    result = commands.web_search("python tutorials", opener=calls.append)
    assert calls == ["https://www.google.com/search?q=python+tutorials"]
    assert "python tutorials" in result


def test_get_time_uses_injected_clock():
    fixed = datetime.datetime(2026, 7, 1, 13, 37)
    assert commands.get_time(fixed) == "Es ist 13:37 Uhr."


def test_get_date_uses_injected_date():
    fixed = datetime.date(2026, 7, 1)
    assert commands.get_date(fixed) == "Heute ist der 01.07.2026."
