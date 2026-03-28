import queue
from pathlib import Path
from typing import Optional

import numpy as np
import sounddevice as sd
import soundfile as sf


def record_to_file(
    filename: str,
    duration: float = 10.0,
    samplerate: int = 16000,
    channels: int = 1,
) -> Path:
    """
    Record audio from the default microphone for a fixed duration
    and save it as a WAV file.

    Returns the Path to the saved file.
    """
    print(f"[Audio] Recording for {duration} seconds...")

    # Record
    recording = sd.rec(
        int(duration * samplerate),
        samplerate=samplerate,
        channels=channels,
        dtype="float32",
    )
    sd.wait()

    # Normalize to int16
    recording_int16 = np.int16(recording * 32767)

    out_path = Path(filename)
    sf.write(out_path, recording_int16, samplerate)
    print(f"[Audio] Saved recording to {out_path}")

    return out_path


def play_wav_file(path: str | Path) -> None:
    """
    Play a WAV file using sounddevice.
    """
    path = Path(path)
    if not path.exists():
        print(f"[Audio] File not found: {path}")
        return

    data, samplerate = sf.read(path, dtype="float32")
    print(f"[Audio] Playing {path}...")
    sd.play(data, samplerate)
    sd.wait()

def record_chunk(
    duration: float = 3.0,
    samplerate: int = 22050,
    channels: int = 1,
) -> np.ndarray:
    """
    Record a short chunk of audio from the default microphone and
    return it as a float32 NumPy array in the range [-1.0, 1.0].

    This does NOT write anything to disk.
    """
    print(f"[Audio] Recording chunk for {duration} seconds...")
    recording = sd.rec(
        int(duration * samplerate),
        samplerate=samplerate,
        channels=channels,
        dtype="float32",
    )
    sd.wait()

    # If mono, flatten to 1D array
    if channels == 1:
        recording = recording.flatten()

    return recording

def record_until_silence(
    samplerate: int = 16000,
    channels: int = 1,
    frame_duration: float = 0.25,      # seconds per small chunk
    max_duration: float = 12.0,        # hard cap so it doesn't record forever
    silence_threshold: float = 0.006,  # how "quiet" counts as silence
    end_silence_seconds: float = 0.8,  # how long of silence ends recording
) -> np.ndarray:
    """
    Record audio from the mic until there has been `end_silence_seconds`
    of silence (volume below `silence_threshold`), or until `max_duration`
    is reached. Returns a float32 NumPy array.

    This is closer to how assistants like Siri behave: it stops when you
    stop talking, not on a fixed timer.
    """
    print("[Audio] Listening for your question (end when you stop talking)...")

    frame_samples = int(frame_duration * samplerate)
    max_frames = int(max_duration / frame_duration)

    frames = []
    silence_time = 0.0

    for i in range(max_frames):
        # Record one small frame
        frame = sd.rec(
            frame_samples,
            samplerate=samplerate,
            channels=channels,
            dtype="float32",
        )
        sd.wait()

        if channels == 1:
            frame = frame.flatten()

        frames.append(frame)

        # Check loudness
        peak = float(abs(frame).max()) if frame.size > 0 else 0.0

        if peak < silence_threshold:
            silence_time += frame_duration
        else:
            silence_time = 0.0   # speaking again → reset silence timer

        # If we've had enough silence after some speech, stop
        total_duration = (i + 1) * frame_duration
        if silence_time >= end_silence_seconds and total_duration > 0.5:
            print(
                f"[Audio] Detected end of speech "
                f"(silence ~{silence_time:.2f}s, total ~{total_duration:.2f}s)."
            )
            break

    if not frames:
        return np.zeros(0, dtype="float32")

    audio = np.concatenate(frames)
    return audio
