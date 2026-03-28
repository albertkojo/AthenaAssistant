from pathlib import Path

from core.config import load_config
from core.llm_client import LLMClient
from core.audio_io import record_to_file
from core.stt import SpeechToText
from core.tts import TextToSpeech


def main() -> None:
    cfg = load_config()

    assistant_cfg = cfg.get("assistant", {})
    llm_cfg = cfg.get("llm", {})
    stt_cfg = cfg.get("stt", {})
    stt_command_cfg = stt_cfg.get("command", {})
                                  
    name = assistant_cfg.get("name", "Athena")
    persona = assistant_cfg.get("persona", "")
    model = llm_cfg.get("model", "llama3.2:3b")
    
    max_history = llm_cfg.get("max_history_messages", 12)
    max_tokens = llm_cfg.get("max_tokens", 256)

    # Initialize components
    client = LLMClient(
        model=model, 
        system_prompt=persona, 
        max_history_messages=max_history, 
        max_tokens=max_tokens
    )
    
    stt = SpeechToText(
        model_size=stt_command_cfg.get("model_size", "small"),
        device=stt_command_cfg.get("device", "cpu"),
        compute_type=stt_command_cfg.get("compute_type", "int8"),
    )

    tts_cfg = cfg.get("tts", {})
    tts = TextToSpeech(
        rate=tts_cfg.get("rate", 180),
        volume=tts_cfg.get("volume", 1.0),
        preferred_keywords=tts_cfg.get("preferred_keywords", ["English"]),
    )

    recordings_dir = Path("recordings")
    recordings_dir.mkdir(exist_ok=True)

    print(f"{name} (voice mode) is online.")
    print("Instructions:")
    print("  Press Enter to record a short message (10 sec).")
    print("  Type 'exit' or 'quit' to leave.\n")

    while True:
        cmd = input(">>> Press Enter to speak, or type 'exit' to quit: ").strip()
        if cmd.lower() in {"exit", "quit"}:
            print("Goodbye.")
            break

        # 1) Record audio
        wav_path = recordings_dir / "last_input.wav"
        record_to_file(str(wav_path), duration=10.0)

        # 2) Transcribe
        try:
            user_text = stt.transcribe_file(wav_path)
        except Exception as e:
            print(f"[Error during STT: {e}]")
            continue

        if not user_text:
            print("[Info] Didn't catch anything. Try speaking more clearly.")
            continue

        print(f"\nYou (transcribed): {user_text}\n")

        # 3) Send to LLM
        try:
            reply = client.ask(user_text)
        except Exception as e:
            print(f"[Error talking to model: {e}]")
            continue

        print(f"{name}: {reply}\n")

        # 4) Speak reply
        try:
            tts.say(reply)
        except Exception as e:
            print(f"[Error during TTS: {e}]")


if __name__ == "__main__":
    main()