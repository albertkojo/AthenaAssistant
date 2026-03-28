from __future__ import annotations

import subprocess


class EdgeTTS:
    """
    Text-to-speech wrapper that uses the `edge-playback` command
    from the `edge-tts` package.

    Uses a neural British voice (e.g. en-GB-SoniaNeural) and relies
    on the default rate/volume to avoid CLI parsing issues.
    """

    def __init__(self, voice: str = "en-GB-SoniaNeural") -> None:
        self.voice = voice

    def say(self, text: str) -> None:
        if not text:
            return

        # Clean basic markdown so she doesn't say "asterisk asterisk"
        cleaned = text.replace("**", "")

        print(f"[TTS] (Edge) Speaking with {self.voice}: {cleaned[:120]!r}...")

        cmd = [
            "edge-playback",
            "--voice",
            self.voice,
            "--text",
            cleaned,
        ]

        try:
            subprocess.run(cmd, check=False)
        except FileNotFoundError:
            print(
                "[TTS] edge-playback command not found. "
                "Make sure `edge-tts` is installed in this virtualenv."
            )
        except Exception as e:
            print(f"[TTS] Error while speaking via edge-playback: {e}")
