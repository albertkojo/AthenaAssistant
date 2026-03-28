from __future__ import annotations

from typing import Optional, List

import pyttsx3


class TextToSpeech:
    def __init__(
        self,
        rate: int = 180,
        volume: float = 1.0,
        preferred_keywords: Optional[List[str]] = None,
    ) -> None:
        """
        Text-to-speech wrapper around pyttsx3.

        We re-initialize the engine per utterance to avoid Windows SAPI
        getting stuck after long responses.
        """
        self.rate = rate
        self.volume = volume
        if preferred_keywords is None:
            preferred_keywords = ["english", "uk", "female"]
        self.preferred_keywords = [k.lower() for k in preferred_keywords]

    def _init_engine(self) -> pyttsx3.Engine:
        """
        Initialize a fresh TTS engine, set rate/volume, and select a voice.
        """
        engine = pyttsx3.init()
        engine.setProperty("rate", self.rate)
        engine.setProperty("volume", self.volume)

        voices = engine.getProperty("voices")

        def voice_matches(v) -> bool:
            text = (v.name + " " + v.id).lower()
            return all(k in text for k in self.preferred_keywords)

        selected = None
        for v in voices:
            if voice_matches(v):
                selected = v
                break

        if selected is None and voices:
            selected = voices[0]

        if selected:
            engine.setProperty("voice", selected.id)
            print(f"[TTS] Using voice: {selected.name} ({selected.id})")
        else:
            print("[TTS] No voices found! TTS may not work correctly.")

        return engine

    def say(self, text: str) -> None:
        """
        Speak the provided text synchronously.
        """
        if not text:
            return

        # Optional: strip markdown-ish junk for cleaner speech
        cleaned = text.replace("**", "")
        # You can add more cleaning rules if needed

        print(f"[TTS] Speaking: {cleaned[:120]!r}...")

        try:
            engine = self._init_engine()
            engine.say(cleaned)
            engine.runAndWait()
            engine.stop()
        except Exception as e:
            print(f"[TTS] Error while speaking: {e}")
