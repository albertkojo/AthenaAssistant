from dataclasses import dataclass, field
from typing import List, Dict, Optional
import ollama


@dataclass
class Message:
    role: str   # "system", "user", or "assistant"
    content: str


@dataclass
class LLMClient:
    model: str
    system_prompt: str = ""
    max_history_messages: int = 12
    max_tokens: Optional[int] = 256
    history: List[Message] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.system_prompt:
            self.history.append(Message("system", self.system_prompt))

    def _build_messages(self) -> List[Dict[str, str]]:
        """
        Build the messages list to send to Ollama, trimming history
        to the last N messages (plus system).
        """
        msgs = self.history

        # Keep system message (if any) and the last `max_history_messages` others
        system_msgs = [m for m in msgs if m.role == "system"]
        other_msgs = [m for m in msgs if m.role != "system"]

        if self.max_history_messages is not None and len(other_msgs) > self.max_history_messages:
            other_msgs = other_msgs[-self.max_history_messages :]

        final_msgs = system_msgs + other_msgs
        return [m.__dict__ for m in final_msgs]

    def ask(self, user_text: str) -> str:
        """
        Send a user message to the LLM and return its reply.
        Conversation history is preserved in self.history, trimmed as needed.
        """
        self.history.append(Message("user", user_text))

        options = {}
        if self.max_tokens is not None:
            options["num_predict"] = self.max_tokens

        response: Dict = ollama.chat(
            model=self.model,
            messages=self._build_messages(),
            options=options,
        )

        assistant_text: str = response["message"]["content"]
        self.history.append(Message("assistant", assistant_text))
        return assistant_text