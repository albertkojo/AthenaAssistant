from pathlib import Path
from typing import Optional

import numpy as np
from faster_whisper import WhisperModel


GHANAIAN_ACCENT_PROMPT = (
    "The speaker pronounces English with a Ghanaian accent, similar to West African English. "
    "Transcribe clearly and accurately in English."
)

class SpeechToText:
    def __init__(
        self,
        model_size: str = "small",
        device: str = "cpu",
        compute_type: str = "int8",
        use_ghanaian_prompt: bool = True,
    ) -> None:
        """
        Initialize the Whisper STT model.

        model_size examples: "tiny", "base", "small", "medium"
        device: "cpu" or "cuda"
        compute_type: "int8", "int16", "float16", etc.
        """
        print(f"[STT] Loading Whisper model '{model_size}' on {device}...")
        self.model = WhisperModel(
            model_size,
            device=device,
            compute_type=compute_type,
        )
        self.use_ghanaian_prompt = use_ghanaian_prompt
        print("[STT] Model loaded.")

    def _run_transcription(self, audio_source) -> str:
        """
        Internal helper to run transcription on either a file path or
        a NumPy array of audio samples.
        """
        kwargs = {
            # Greedy decoding: much faster than beam search
            "beam_size": 1,
            "best_of": 1,
            "without_timestamps": True,
        }

        if self.use_ghanaian_prompt:
            kwargs["initial_prompt"] = GHANAIAN_ACCENT_PROMPT

        segments, info = self.model.transcribe(audio_source, **kwargs)

        texts = [segment.text for segment in segments]
        full_text = " ".join(texts).strip()
        print(f"[STT] Transcription: {full_text!r}")
        return full_text


    def transcribe_file(self, audio_path: str | Path) -> str:
        """
        Transcribe an audio file and return the text.
        """
        audio_path = Path(audio_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        print(f"[STT] Transcribing file {audio_path}...")
        return self._run_transcription(str(audio_path))

    def transcribe_array(self, audio: np.ndarray) -> str:
        """
        Transcribe an in-memory audio array (float32, 16 kHz) and return the text.
        """
        if audio is None or audio.size == 0:
            return ""

        print(f"[STT] Transcribing in-memory audio array of shape {audio.shape}...")
        return self._run_transcription(audio)
