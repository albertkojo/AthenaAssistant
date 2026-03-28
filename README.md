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
Establish the baseline text-to-action pipeline.

* **Objective:** Connect the Gemini 1.5 Flash API to your local Windows environment for basic OS control.

* **Components:** Python (os, subprocess), Google GenAI SDK.

* **Target Capabilities:**

    * Define functions for opening applications, managing windows, and basic system queries.

    * Implement strict JSON schema parsing to translate the LLM output into executable Python code.

* **Milestone:** Text input successfully triggers local desktop actions.

### Phase 2: Audio Pipeline Integration
Implement local voice ingestion and cloud synthesis to minimize latency.

* **Objective:** Establish reliable, hands-free communication.

* **Components:** Picovoice Porcupine, faster-whisper, edge-tts, pyaudio.

* **Target Capabilities:**

    * Run a lightweight background thread listening for the "Athena" wake word.

    * Load the Whisper model into your 32 GB of system RAM for fast, local speech-to-text.

    * Stream the text response back through edge-tts.

* **Milestone:** Voice input executes a command, and the system verbally confirms completion.

### Phase 3: Development Automation & Vision
Integrate engineering-specific workflows and screen awareness.

* **Objective:** Automate workspace setup and debug assistance.

* **Components:** mss or Pillow (screen capture), CLI wrappers.

* **Target Capabilities:**

    * Pass base64 encoded screen captures to Gemini’s multimodal endpoint for code error analysis.

    * Create multi-step macro tools: e.g., a single command to open VS Code, launch the Android emulator, and run flutter run for The Override.

    * Pipe compilation errors (stderr) directly back to the LLM for automated troubleshooting.

* **Milestone:** Athena visually identifies an error on your screen and executes the necessary CLI commands to recompile a project.

### Phase 4: Proactive Monitoring & Long-Term Memory
Transition the system from reactive to proactive.

* **Objective:** Enable hardware telemetry and persistent context.

* **Components:** psutil, ChromaDB (local vector database), Google Calendar API.

* **Target Capabilities:**

    * Run asynchronous threads to monitor system states. Athena verbally interrupts if the i7-10750H temperature exceeds 85°C.

    * Store conversation summaries in ChromaDB to recall technical decisions across reboots.

    * Parse scheduled events to provide automated briefings on upcoming commitments, such as deadlines for the SoutheastCon circuits competition.

* **Milestone:** Athena recalls a technical parameter from a session two days prior and warns you of high CPU temperatures while running an emulator.

### Phase 5: Logistics & Media Control
Connect external data sources for environment and routine management.

* **Objective:** Handle daily logistics outside the local OS.

* **Components:** Google Maps API, Weather API, Spotify Web API, local REST endpoints.

* **Target Capabilities:**

    * Query traffic conditions dynamically to calculate precise commute times from Bloomington.

    * Control media playback (e.g., queuing tech podcasts) via API requests to bypass desktop UI limitations.

    * Send commands to local network devices (smart plugs, lighting) if applicable.

* **Milestone:** A single voice command pauses a podcast, checks local weather, and estimates drive time for your next calendar event.

### Phase 6: Headless Automation & Publishing
Deploy web scrapers and headless browsers for complex web tasks.

* **Objective:** Automate repetitive online interactions.

* **Components:** Playwright (headless), BeautifulSoup, Social Media APIs (e.g., Instagram Graph API).

* **Target Capabilities:**

    * Execute Playwright scripts to navigate delivery portals and reorder frequent items (e.g., Dry Pot Beef from Spicity with specific modifiers).

    * Monitor specific URLs for updates and store the diffs in a local SQLite database.

    * Monitor a local directory; when a text file is added, format it, generate tags, and push it live to gentlevoid.poetry.

* **Milestone:** Athena completes a multi-step web transaction or publishes content without any manual browser interaction.