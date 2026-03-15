# 🤖 MegaBox — Local AI Voice Assistant

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Ollama](https://img.shields.io/badge/LLM-Ollama-black?logo=ollama&logoColor=white)](https://ollama.ai/)
[![Voice](https://img.shields.io/badge/Voice-Enabled-9cf?logo=amazon-alexa&logoColor=white)]()
[![Status](https://img.shields.io/badge/Status-Prototype-orange)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> **MegaBox** is a fully local AI voice assistant built in Python that can talk, think, remember context, and take real actions on your computer — powered by a local LLM via Ollama, with no cloud dependency.

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Main Features](#-main-features)
- [System Architecture](#-system-architecture)
- [Technologies Used](#-technologies-used)
- [Installation](#-installation)
- [How to Run](#-how-to-run)
- [Example Commands](#-example-commands)
- [Project Structure](#-project-structure)
- [Future Improvements](#-future-improvements)
- [Project Status](#-project-status)
- [Author](#-author)
- [License](#-license)

---

## 🔍 Overview

**MegaBox** is an experimental local AI assistant that combines conversational intelligence, voice interaction, memory, and system automation into a single Python application. Unlike cloud-based assistants, MegaBox runs entirely on your local machine using [Ollama](https://ollama.ai/) as its LLM backend — keeping everything private and offline.

It can hold a natural conversation, remember what you've said, respond with a voice, and actually perform tasks on your computer like opening apps, playing music, controlling the browser, and more.

---

## ✨ Main Features

### 🧠 Conversational AI
- Powered by a **local LLM via Ollama** — fully offline, no API keys needed
- Maintains **conversation context** across the session
- Produces natural, intelligent dialogue responses

### 🎙️ Voice Interaction
- **Speech recognition** via microphone input
- **Text-to-speech** voice output using pyttsx3
- Supports both **voice and keyboard** input modes

### 💾 Memory System
- Stores full **conversation history**
- Tracks a **user profile** across sessions
- Simulates an **internal thought stream** for more coherent responses

### ⚙️ System Automation
MegaBox can directly control your computer:

| Action | Example Command |
|---|---|
| Open applications | *"open notepad"* |
| Control the browser | *"open youtube"* |
| Play songs | *"play believer"* |
| Play YouTube videos | *"play funny video on youtube"* |
| Search the internet | *"search artificial intelligence"* |
| Close programs | *"close chrome"* |
| Control brightness | *"increase brightness"* |
| Switch windows | *"switch window"* |
| Close tabs | *"close tab"* |

### 🗂️ Planning Engine
Complex, multi-step requests are handled by a built-in **task planner** that breaks down the request into individual steps and executes them in sequence — enabling more autonomous behaviour.

---

## 🏗️ System Architecture

![MegaBox Architecture](https://github.com/user-attachments/assets/b4e3e69c-3a2a-45a5-8ae6-43298b50a793)

At a high level, MegaBox operates through the following pipeline:

```
┌──────────────────────────────────────────────────────────────┐
│                        USER INPUT                            │
│              Voice (microphone) or Keyboard                  │
└─────────────────────────┬────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────────┐
│                   SPEECH RECOGNITION                         │
│            Converts voice input to text                      │
└─────────────────────────┬────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────────┐
│                  LOCAL LLM  (Ollama)                         │
│   Understands intent · Maintains context · Plans response    │
└──────────┬───────────────────────────────┬───────────────────┘
           │                               │
           ▼                               ▼
┌─────────────────────┐        ┌───────────────────────────────┐
│   TASK PLANNER      │        │        MEMORY SYSTEM          │
│  Breaks complex     │        │  Conversation history         │
│  requests into      │        │  User profile                 │
│  executable steps   │        │  Thought stream               │
└──────────┬──────────┘        └───────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────────┐
│                   SYSTEM AUTOMATION                          │
│   PyAutoGUI · Browser control · App launcher · Media        │
└─────────────────────────┬────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────────┐
│                    VOICE RESPONSE                            │
│              pyttsx3 text-to-speech output                   │
└──────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Technologies Used

| Technology | Role |
|---|---|
| **Python 3.9+** | Core language |
| **Ollama** | Local LLM backend (runs AI model offline) |
| **SpeechRecognition** | Converts microphone input to text |
| **pyttsx3** | Text-to-speech voice output |
| **PyAutoGUI** | System automation and GUI control |
| **Requests** | HTTP requests for internet search / APIs |

---

## ⚙️ Installation

### Prerequisites

- Python 3.9 or higher
- [Ollama](https://ollama.ai/) installed and running locally
- A working microphone (for voice input)

### 1. Clone the repository

```bash
git clone https://github.com/saurabhsharma1122/megabox-ai-assistant.git
cd megabox-ai-assistant
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4. Start Ollama

Make sure Ollama is installed and a model is running before launching MegaBox:

```bash
ollama run llama3
```

> Replace `llama3` with whichever model you have pulled locally.

---

## 🚀 How to Run

```bash
python main.py
```

MegaBox will start and prompt you for input. You can interact using:
- 🎙️ **Voice** — speak into your microphone
- ⌨️ **Keyboard** — type your command when prompted

---

## 💬 Example Commands

```
"play believer"
"play a song"
"open youtube"
"play funny video on youtube"
"close chrome"
"search artificial intelligence"
"open notepad"
"increase brightness"
"switch window"
```

MegaBox understands natural phrasing — you don't need to use exact keywords.

---

## 📁 Project Structure

```
megabox-ai-assistant/
│
├── main.py                  # Entry point — starts MegaBox
├── requirements.txt         # Python dependencies
│
├── assistant/
│   ├── brain.py             # LLM interaction via Ollama
│   ├── voice.py             # Speech recognition + TTS
│   ├── memory.py            # Conversation history + user profile
│   └── planner.py           # Task planning engine
│
├── automation/
│   ├── system_control.py    # App launcher, brightness, windows
│   ├── browser_control.py   # Chrome / browser automation
│   └── media_control.py     # Music, YouTube playback
│
└── README.md
```

> Update this section to match your actual file layout.

---

## 🔮 Future Improvements

- [ ] **GUI Dashboard** — Visual interface to monitor MegaBox activity
- [ ] **Wake Word Detection** — Always-on listening with a trigger word (e.g. *"Hey Mega"*)
- [ ] **Long-term Memory** — Persist memory across restarts using a local database
- [ ] **More System Controls** — Volume, screen recording, file management
- [ ] **Emotion Detection** — Adjust responses based on tone of voice
- [ ] **Multi-model Support** — Swap between different Ollama models on the fly
- [ ] **Plugin System** — Let users add custom skills and commands
- [ ] **Mobile Companion App** — Control MegaBox remotely from your phone

---

## 📊 Project Status

![Project Status](https://github.com/user-attachments/assets/c1f9c315-1d6b-467b-b4e6-aeaf0534c2e7)

MegaBox is an **experimental prototype** actively exploring:

- Autonomous AI behaviour on a local machine
- Multi-step task planning and execution
- Human-AI interaction through natural voice dialogue

More capabilities and improvements will be added in future updates.

---

## 👤 Author

**Saurabh Sharma**
Department of Computer Science & Engineering

- GitHub: [@saurabhsharma1122](https://github.com/saurabhsharma1122)

---

## 📜 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgements

- [Ollama](https://ollama.ai/) — Local LLM runtime
- [SpeechRecognition](https://pypi.org/project/SpeechRecognition/) — Voice input library
- [pyttsx3](https://pypi.org/project/pyttsx3/) — Offline text-to-speech
- [PyAutoGUI](https://pypi.org/project/PyAutoGUI/) — System automation

---

*If you find MegaBox useful or interesting, give it a ⭐ on GitHub!*
