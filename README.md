# Athena: Hybrid OS Personal Assistant
**Author**: Albert Essiaw

**Version**: 0.1.0 (*Pre-Alpha*)

## System Requirements
* **OS:** Windows 11 Home (Version 25H2)
* **CPU:** Intel Core i7-10750H
* **RAM:** 32.0 GB 
* **Dependencies:** Python 3.10+, Google AI Studio API Key, Picovoice Access Key.

## Project Overview
Athena is a voice-activated, multimodal desktop assistant engineered for autonomus operating system control and task automation.

Due to local hardware constraints, specifically a 4 GB GPU VRAM bottleneck, a fully local Large Language Model (LLM) deployment is unviable for complex tool execution. Athena utilizes a **Hybrid Architecture**: local hardware handles memory-intensive audio ingestion and processing, while high-speed cloud APIs process logic and state management.

## System Architecture
| Component | Function | Technology | Environment |
| :--- | :--- | :--- | :--- |
| **Wake Word Engine** | Passive listening | Picovoice Porcupine | Local |
| **Speech-to-Text (STT)** | Voice transcription | `faster-whisper` | Local (System RAM) |
| **Logic Core (LLM)** | Intent parsing & tool selection | Gemini 1.5 Flash API | Cloud |
| **Action Layer** | OS command execution | Python (`os`, `subprocess`) | Local |
| **Text-to-Speech (TTS)** | Voice synthesis | `edge-tts` | Cloud |
| **Memory & Context** | Persistent state storage | ChromaDB | Local |

## Hardware Profile Target
* **OS:** Windows 11 Home (Build 26200.8039)
* **CPU:** Intel Core i7-10750H (Note: Active thermal monitoring required during local model execution).
* **RAM:** 32.0 GB (Utilized for loading Whisper models and headless browser instances).
* **GPU:** 4.0 GB VRAM (Bypassed via Gemini API for logic core).

## Implementation Roadmap

### Phase 1: Core Logic & Base Tool Execution
* Connect Gemini API to the local environment using the Google GenAI SDK.
* Define Python functions for OS control (window management, process execution).
* Implement JSON schema parsing for strict tool calling.

### Phase 2: Audio Pipeline Integration
* Initialize Porcupine background thread for the "Athena" wake word.
* Load Whisper model into system memory.
* Stream text output through `edge-tts` for low-latency voice response.

### Phase 3: Development Automation & Vision
* Integrate `mss` for base64 screen capture and multimodal code error analysis.
* Automate workspace initialization (launch VS Code, Android emulator).
* Implement CLI wrappers to pipe compilation errors (e.g., `flutter run` for The Override) directly back to the logic core.

### Phase 4: Proactive Monitoring & Long-Term Memory
* Deploy asynchronous threads via `psutil` for hardware telemetry.
* Set interrupt thresholds to trigger verbal warnings if the CPU temperature exceeds 85°C.
* Initialize ChromaDB for persistent context retrieval across sessions.
* Integrate Google Calendar API to parse schedules, prioritizing deadlines for the IEEE SoutheastCon 2026 circuit competition.

### Phase 5: Logistics & Media Control
* Connect Google Maps API to calculate commute metrics and drive times from Bloomington.
* Integrate Spotify Web API for headless media playback.

### Phase 6: Headless Automation & Publishing
* Deploy Playwright scripts for automated web transactions, such as portal navigation and reordering from Spicity.
* Configure local directory watchers to format text files, generate tags, and push content directly to gentlevoid.poetry via social media APIs.