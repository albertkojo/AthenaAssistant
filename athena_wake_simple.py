from __future__ import annotations

import difflib
import sys
import time

from core.config import load_config
from core.llm_client import LLMClient
from core.audio_io import record_chunk
from core.stt import SpeechToText
from core.tts_edge import EdgeTTS as TextToSpeech


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
    stt_cmd_cfg = cfg.get("stt", {}).get("command", {})
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

    # Single, strong STT model for both wake + question
    stt = SpeechToText(
        model_size=stt_cmd_cfg.get("model_size", "medium.en"),
        device=stt_cmd_cfg.get("device", "cpu"),
        compute_type=stt_cmd_cfg.get("compute_type", "int8"),
        use_ghanaian_prompt=True,   # helps hear your accent correctly
    )

    # TTS with UK female preference (we’ll improve the actual voice later)
    # FRIDAY-style British neural voice via Edge-TTS
    tts = TextToSpeech(
        voice=tts_cfg.get("voice", "en-GB-SoniaNeural"),
    )

    chunk_duration = stt_cmd_cfg.get("chunk_duration", 4.0)
    silence_threshold = stt_cmd_cfg.get("silence_threshold", 0.02)
    samplerate = stt_cmd_cfg.get("sample_rate", 16000)
    followup_timeout = stt_cmd_cfg.get("followup_timeout", 18.0)

    # Conversation state
    conversation_active_until = 0.0

    print(f"{name} simple wake mode (one-model) is online.")
    print(f"Wake word: '{wake_word}'")
    print("Say something like: 'Athena, what is a CPU?'")
    print("After she answers, you can ask a follow-up without saying 'Athena'.")
    print("Press Ctrl+C to stop.\n")

    try:
        while True:
            now = time.time()

            # 1) Record a short chunk
            audio = record_chunk(
                duration=chunk_duration,
                samplerate=samplerate,
                channels=1,
            )

            # 2) Silence filter
            peak = float(abs(audio).max()) if audio.size > 0 else 0.0
            if peak < silence_threshold:
                continue

            # 3) Transcribe
            try:
                transcript = stt.transcribe_array(audio)
            except Exception as e:
                print(f"[Error during STT: {e}]")
                continue

            if not transcript:
                continue

            lower = transcript.lower()

            # If it's super short, probably noise
            if len(lower.split()) < 2:
                continue

            print(f"[Heard] {transcript!r}")

            user_text = None

            # --- CASE A: follow-up within timeout (no wake word needed) ---
            if now < conversation_active_until:
                user_text = transcript.strip()

            # --- CASE B: explicit wake word ---
            elif fuzzy_match(wake_word, lower, cutoff=0.7):
                user_text = strip_wake_word(transcript, wake_word)
                if not user_text or len(user_text.split()) < 2:
                    # If nothing meaningful after wake word, ignore
                    user_text = None

            if not user_text:
                # Not a follow-up or wake-initiated command; ignore
                continue

            print(f"\nYou: {user_text}\n")

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

            # 6) Open follow-up window
            conversation_active_until = time.time() + followup_timeout

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n[Info] Stopping simple wake mode. Goodbye.")
        sys.exit(0)


if __name__ == "__main__":
    main()
