# Athena: Hybrid OS Personal Assistant
**Author**: Albert Essiaw

**Version**: 0.1.0 (*Pre-Alpha*)

**Target OS**: Windows 11

## Project Overview
Athena is a voice-activated, multimodal desktop assistant engineered for autonomus operating system control and task automation.

Due to local hardware constraints, specifically a 4 GB GPU VRAM bottleneck, a fully local Large Language Model (LLM) deployment is unviable for complex tool execution. Athena utilizes a **Hybrid Architecture**: local hardware handles memory-intensive audio ingestion and processing, while high-speed cloud APIs process logic and state management.

## System Architecture
|Component|Function|Technology,|Execution
Wake Word,|Passive listening engine,|Picovoice Porcupine, |Local (CPU)
STT|,Speech-to-Text|,faster-whisper,|Local (System RAM)
Logic Core,Intent parsing & tool calling,Gemini 1.5 Flash API,Cloud
Action Layer,OS execution,"Python (subprocess, os)",Local
TTS,Text-to-Speech,edge-tts,Cloud