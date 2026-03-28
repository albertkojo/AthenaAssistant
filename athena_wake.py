from __future__ import annotations

import difflib
import sys
import time

from core.config import load_config
from core.llm_client import LLMClient
from core.audio_io import record_chunk
from core.stt import SpeechToText
from core.tts import TextToSpeech
from core.audio_io import record_until_silence


def strip_wake_word(text: str, wake_word: str) -> str:
    """
    Remove the first occurrence of the wake word from the text,
    and return the remaining string cleaned up.
    """
    text_low = text.lower()
    wake_low = wake_word.lower()

    idx = text_low.find(wake_low)
    if idx == -1:
        # Wake word not found; return original text
        return text.strip()

    # Everything after the wake word
    start = idx + len(wake_low)
    remaining = text[start:]
    # Clean up common punctuation / spaces
    return remaining.lstrip(" ,.:;!?").strip()


def fuzzy_match(word: str, text: str, cutoff: float = 0.7) -> bool:
    """
    Check if any word in 'text' is a fuzzy match for 'word' with at least `cutoff`
    similarity (0.0–1.0). Helps with accented pronunciations of the wake word.
    """
    text_words = text.lower().split()
    target = word.lower()

    for w in text_words:
        ratio = difflib.SequenceMatcher(None, w, target).ratio()
        if ratio >= cutoff:
            # print(f"[Wake] Fuzzy match '{w}' ~ '{target}' ({ratio:.2f})")
            return True
    return False


def main() -> None:
    cfg = load_config()

    assistant_cfg = cfg.get("assistant", {})
    llm_cfg = cfg.get("llm", {})
    stt_cfg = cfg.get("stt", {})
    stt_wake_cfg = stt_cfg.get("wake", {})
    stt_cmd_cfg = stt_cfg.get("command", {})
    tts_cfg = cfg.get("tts", {})

    name = assistant_cfg.get("name", "Athena")
    wake_word = assistant_cfg.get("wake_word", "athena").lower()
    persona = assistant_cfg.get("persona", "")

    model = llm_cfg.get("model", "llama3.2:3b")
    max_history = llm_cfg.get("max_history_messages", 12)
    max_tokens = llm_cfg.get("max_tokens", 256)

    # LLM client
    client = LLMClient(
        model=model,
        system_prompt=persona,
        max_history_messages=max_history,
        max_tokens=max_tokens,
    )

    # STT for wake listening - tiny model
    stt_wake = SpeechToText(
    model_size=stt_wake_cfg.get("model_size", "tiny"),
    device=stt_wake_cfg.get("device", "cpu"),
    compute_type=stt_wake_cfg.get("compute_type", "int8"),
    use_ghanaian_prompt=False,   # ⬅️ no accent prompt for wake loop
)

    # STT for actual commands - medium.en model
    stt_cmd = SpeechToText(
        model_size=stt_cmd_cfg.get("model_size", "medium.en"),
        device=stt_cmd_cfg.get("device", "cpu"),
        compute_type=stt_cmd_cfg.get("compute_type", "int8"),
        use_ghanaian_prompt=True,
    )

    # TTS with UK female preference
    tts = TextToSpeech(
        rate=tts_cfg.get("rate", 185),
        volume=tts_cfg.get("volume", 0.9),
        preferred_keywords=tts_cfg.get(
            "preferred_keywords",
            ["english", "uk", "female"],
        ),
    )

    # Wake listening settings
    wake_chunk_duration = stt_wake_cfg.get("chunk_duration", 3.0)
    wake_silence_threshold = stt_wake_cfg.get("silence_threshold", 0.008)
    wake_samplerate = stt_wake_cfg.get("sample_rate", 22050)

    # Command listening settings (Siri-style)
    cmd_max_duration = stt_cmd_cfg.get("max_duration", 12.0)
    cmd_samplerate = stt_cmd_cfg.get("sample_rate", 16000)
    cmd_end_silence = stt_cmd_cfg.get("end_silence_seconds", 0.8)
    followup_timeout = stt_cmd_cfg.get("followup_timeout", 18.0)


    # Conversation state
    conversation_active_until = 0.0

    print(f"{name} always-listening mode (2-stage, accent-optimized) is online.")
    print(f"Wake word: '{wake_word}'")
    print("Say something like: 'Athena, what is a CPU?'")
    print("After she answers, you can ask ONE follow-up question without saying 'Athena'.")
    print("Press Ctrl+C to stop.\n")

    try:
        while True:
            now = time.time()

            # 1) Record a short in-memory chunk for wake/follow-up detection
            audio = record_chunk(
                duration=wake_chunk_duration,
                samplerate=wake_samplerate,
                channels=1,
            )

            # 2) Basic silence detection
            peak = float(abs(audio).max()) if audio.size > 0 else 0.0
            if peak < wake_silence_threshold:
                continue

            # 3) Transcribe the chunk with wake STT
            try:
                transcript = stt_wake.transcribe_array(audio)
            except Exception as e:
                print(f"[Error during STT (wake): {e}]")
                continue

            if not transcript:
                continue

            lower = transcript.lower()

            # Ignore junk where Whisper is just echoing our own initial prompt
            if "ghanaian accent" in lower or "transcribe clearly and accurately in english" in lower:
            # print("[Wake] Ignoring prompt-echo garbage.")
                continue

            print(f"[Heard] {transcript!r}")

            # --- CASE A: follow-up within timeout, no wake word needed ---
            if now < conversation_active_until and len(lower.split()) >= 3:
                user_text = transcript.strip()
                print(f"\n[Follow-up] Using transcript as question: {user_text!r}\n")

            # --- CASE B: explicit wake word (first question) ---
            elif fuzzy_match(wake_word, transcript, cutoff=0.7):
                print("[Wake] Detected wake word, recording your question with better model...")

                # Record a fresh chunk for the actual question using command STT settings
                cmd_audio = record_until_silence(
                    samplerate=cmd_samplerate,
                    channels=1,
                    max_duration=cmd_max_duration,
                    silence_threshold=wake_silence_threshold,
                    end_silence_seconds=cmd_end_silence,
                )

                if cmd_audio.size == 0:
                    print("[Info] Did not capture any question audio.")
                    continue

                cmd_peak = float(abs(cmd_audio).max())
                if cmd_peak < wake_silence_threshold:
                    print("[Info] Question audio too quiet, skipping.")
                    continue

                try:
                    cmd_text = stt_cmd.transcribe_array(cmd_audio)
                except Exception as e:
                    print(f"[Error during STT (command): {e}]")
                    continue

                if not cmd_text:
                    print("[Info] Did not catch your actual question.")
                    continue

                # Strip the wake word if it appears inside
                user_text = strip_wake_word(cmd_text, wake_word)
                if not user_text:
                    user_text = cmd_text.strip()

                if len(user_text.split()) < 2:
                    continue

                print(f"\nYou (via wake word): {user_text}\n")

            else:
                # No wake word, no follow-up
                continue

            # 4) Send to LLM
            try:
                reply = client.ask(user_text)
            except Exception as e:
                print(f"[Error talking to model: {e}]")
                continue

            print(f"{name}: {reply}\n")

            # 5) Speak reply
            try:
                tts.say(reply)
            except Exception as e:
                print(f"[Error during TTS: {e}]")

            # 6) Open a follow-up window
            conversation_active_until = time.time() + followup_timeout

            # Small pause
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n[Info] Stopping always-listening mode. Goodbye.")
        sys.exit(0)


if __name__ == "__main__":
    main()
