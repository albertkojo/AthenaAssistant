from core.config import load_config
from core.llm_client import LLMClient


def main() -> None:
    cfg = load_config()

    assistant_cfg = cfg.get("assistant", {})
    llm_cfg = cfg.get("llm", {})

    name = assistant_cfg.get("name", "Athena")
    persona = assistant_cfg.get("persona", "")
    model = llm_cfg.get("model", "llama3.2:3b")
    max_history = llm_cfg.get("max_history_messages", 12)
    max_tokens = llm_cfg.get("max_tokens", 256)

    client = LLMClient(
        model=model, 
        system_prompt=persona, 
        max_history_messages=max_history, 
        max_tokens=max_tokens
    )

    print(f"{name} is online. Type 'exit' or 'quit' to leave.\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting. Goodbye.")
            break

        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye.")
            break

        if not user_input:
            continue

        try:
            reply = client.ask(user_input)
        except Exception as e:  # very broad for now; we’ll refine later
            print(f"[Error talking to model: {e}]")
            continue

        print(f"\n{name}: {reply}\n")


if __name__ == "__main__":
    main()