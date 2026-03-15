# 🧠 MegaBox — Autonomous Cognitive AI Assistant

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Ollama](https://img.shields.io/badge/LLM-Ollama-black?logoColor=white)](https://ollama.ai/)
[![LLaMA3](https://img.shields.io/badge/Model-LLaMA3-blueviolet)]()
[![Qwen](https://img.shields.io/badge/Model-Qwen--Coder-orange)]()
[![Voice](https://img.shields.io/badge/Voice-Enabled-9cf)]()
[![Status](https://img.shields.io/badge/Status-Experimental-yellow)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> **MegaBox** is an experimental autonomous AI assistant built in Python — designed to think, remember, feel, plan, and act. It goes far beyond a simple chatbot, operating as a cognitive system with internal reasoning, emotional state modeling, multi-model AI routing, proactive initiative, and full system control — all running entirely on your local machine.

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Core Modules](#-core-modules)
- [Installation Guide](#-installation-guide)
- [Requirements](#-requirements)
- [How to Run](#-how-to-run)
- [Example Interaction](#-example-interaction)
- [Project Structure](#-project-structure)
- [Future Improvements](#-future-improvements)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🔍 Overview

MegaBox is not a chatbot. It is a **cognitive AI assistant** — a system that models its own internal state, reasons through problems before responding, maintains layered memory across sessions, and proactively initiates actions without always waiting to be asked.

It runs **100% locally** using [Ollama](https://ollama.ai/) as the LLM backend, routing requests intelligently between **LLaMA3** for conversation and **Qwen Coder** for technical tasks. There is no cloud, no API key, no data leaving your machine.

MegaBox was built to explore what a truly autonomous, self-aware AI assistant might look like — one that has moods, beliefs, curiosity, and a sense of self — not just a prompt-response loop.

---

## ✨ Key Features

| Category | Capability |
|---|---|
| 🎙️ **Voice Interface** | Speaks and listens — full voice conversation support |
| 🧠 **Multi-Model AI** | Routes between LLaMA3 (conversation) and Qwen Coder (technical) |
| 💾 **Layered Memory** | Short-term, long-term, and recalled memory with a memory governor |
| 🪞 **Internal Mind** | Generates internal thoughts before responding — reasoning before speaking |
| 😌 **Self-State Model** | Tracks mood, energy, curiosity, engagement, focus, and stability |
| 🔁 **Reflection Engine** | Periodically reflects on conversations and updates beliefs |
| 🚀 **Proactive Initiative** | Takes actions without being asked when the context calls for it |
| 📅 **Event System** | Manages reminders, alarms, birthdays, and scheduled tasks |
| ⚙️ **System Automation** | Opens apps, controls browser, plays media, manages windows |
| 👤 **User Profiling** | Learns user preferences and adapts its behaviour over time |

---

## 🏗️ System Architecture

MegaBox is composed of six interconnected subsystems that work in concert on every interaction:

```
╔══════════════════════════════════════════════════════════════════════╗
║                        USER INTERACTION                              ║
║              🎙️  Voice Input   /   ⌨️  Keyboard Input               ║
╚══════════════════════════════╦═══════════════════════════════════════╝
                               ║
                               ▼
╔══════════════════════════════════════════════════════════════════════╗
║                      VOICE INTERFACE LAYER                           ║
║        voice_listener  ──────────────────  voice_speaker             ║
║     (SpeechRecognition)                    (pyttsx3 TTS)             ║
╚══════════════════════════════╦═══════════════════════════════════════╝
                               ║
               ┌───────────────╩───────────────┐
               ▼                               ▼
╔══════════════════════════╗   ╔═══════════════════════════════════════╗
║    COGNITIVE SYSTEMS     ║   ║          MEMORY SYSTEMS               ║
║                          ║   ║                                       ║
║  internal_mind           ║   ║  memory.json  (short-term)            ║
║  (internal thoughts)     ║   ║  long_memory.json  (long-term)        ║
║                          ║   ║  recall_engine  (retrieval)           ║
║  self_state model        ║   ║  memory_governor  (management)        ║
║  mood / energy /         ║   ║                                       ║
║  curiosity / focus /     ║   ╚═══════════════════════════════════════╝
║  engagement / stability  ║
║                          ║
║  reflection_engine       ║
║  introspection_engine    ║
║  initiative_engine       ║
║  belief_engine           ║
╚══════════════╦═══════════╝
               ║
               ▼
╔══════════════════════════════════════════════════════════════════════╗
║                     CONVERSATION BRAIN                               ║
║                          brain.py                                    ║
║                                                                      ║
║          ┌─────────────────────────────────────────┐                ║
║          │         Multi-Model Router               │                ║
║          │                                          │                ║
║          │  LLaMA3 ◄──── conversation / reasoning  │                ║
║          │  Qwen Coder ◄─ code / technical tasks    │                ║
║          └─────────────────────────────────────────┘                ║
╚══════════════════════════════╦═══════════════════════════════════════╝
                               ║
               ┌───────────────╩───────────────┐
               ▼                               ▼
╔══════════════════════════╗   ╔═══════════════════════════════════════╗
║    PREFERENCE & PROFILE  ║   ║          ACTION SYSTEM                ║
║                          ║   ║                                       ║
║  preference_engine       ║   ║  planner_engine                       ║
║  profile_engine          ║   ║    └─ breaks requests into steps      ║
║                          ║   ║  action_engine                        ║
╚══════════════════════════╝   ║    └─ decides what to execute         ║
                               ║  action_executor                      ║
╔══════════════════════════╗   ║    └─ carries out the action          ║
║      EVENT SYSTEM        ║   ║  system_controller                    ║
║                          ║   ║    └─ OS-level automation             ║
║  event_engine            ║   ║                                       ║
║  reminders / alarms /    ║   ╚═══════════════════════════════════════╝
║  birthdays / tasks       ║
╚══════════════════════════╝
                               ║
                               ▼
╔══════════════════════════════════════════════════════════════════════╗
║                         VOICE RESPONSE                               ║
║                  pyttsx3  text-to-speech output                      ║
╚══════════════════════════════════════════════════════════════════════╝
```

### How It All Connects

When you speak to MegaBox, this is what happens internally before it ever replies:

1. `voice_listener` captures your speech and converts it to text
2. `recall_engine` searches memory for relevant past context
3. `internal_mind` generates a private internal thought — MegaBox reasons before it speaks
4. `self_state` is checked — its current mood, energy, and curiosity influence the response tone
5. `brain.py` routes the request to LLaMA3 or Qwen Coder depending on task type
6. `belief_engine` and `reflection_engine` update based on the conversation
7. If action is needed, `planner_engine` → `action_engine` → `action_executor` → `system_controller`
8. `memory_governor` decides what gets stored in short vs. long-term memory
9. `voice_speaker` delivers the final response

---

## 🔧 Core Modules

### 🎙️ Voice Interface
| Module | Role |
|---|---|
| `voice_listener` | Captures microphone input and converts speech to text using SpeechRecognition |
| `voice_speaker` | Converts text responses to spoken audio using pyttsx3 |

### 🧠 Conversation Brain
| Module | Role |
|---|---|
| `brain.py` | Central LLM orchestrator — builds prompts, manages context, calls Ollama |
| Multi-model router | Sends general queries to **LLaMA3**, code/technical queries to **Qwen Coder** |

### ⚙️ Action System
| Module | Role |
|---|---|
| `planner_engine` | Breaks complex multi-step requests into an ordered execution plan |
| `action_engine` | Determines which actions are needed for a given intent |
| `action_executor` | Carries out the planned actions |
| `system_controller` | OS-level control: apps, browser, media, windows, brightness |

### 💾 Memory Systems
| Module | Role |
|---|---|
| `memory.json` | Short-term conversation history for the current session |
| `long_memory.json` | Persistent long-term memory stored across restarts |
| `recall_engine` | Retrieves relevant memories based on current context |
| `memory_governor` | Decides what to store, consolidate, or forget |

### 🪞 Cognitive Systems
| Module | Role |
|---|---|
| `internal_mind` | Generates private internal thoughts before each response |
| `self_state` | Models mood, energy, curiosity, engagement, focus, and stability |
| `initiative_engine` | Enables MegaBox to proactively act without being asked |
| `belief_engine` | Maintains and updates MegaBox's beliefs based on interactions |
| `reflection_engine` | Periodically reflects on past exchanges to improve responses |
| `introspection_engine` | Allows MegaBox to reason about its own internal states |

### 📅 Event System
| Module | Role |
|---|---|
| `event_engine` | Manages time-based events: reminders, alarms, birthdays, tasks |

### 👤 Preference & Profile
| Module | Role |
|---|---|
| `preference_engine` | Tracks and applies user preferences to personalise responses |
| `profile_engine` | Builds and maintains a persistent user profile over time |

---

## ⚙️ Installation Guide

### Prerequisites

- Python **3.9** or higher
- [Ollama](https://ollama.ai/) installed and running locally
- A working **microphone** for voice input
- Windows / macOS / Linux

### Step 1 — Clone the repository

```bash
git clone https://github.com/saurabhsharma1122/megabox-ai-assistant.git
cd megabox-ai-assistant
```

### Step 2 — Create a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Pull the required Ollama models

```bash
# Conversational reasoning model
ollama pull llama3

# Code and technical tasks model
ollama pull qwen2.5-coder
```

### Step 5 — Start Ollama

```bash
ollama serve
```

> Keep this running in a separate terminal. MegaBox connects to it automatically.

---

## 📦 Requirements

```
speechrecognition
pyttsx3
pyautogui
requests
ollama
pyaudio
```

Install everything at once:

```bash
pip install -r requirements.txt
```

> **Windows users:** If `pyaudio` fails to install, use:
> ```bash
> pip install pipwin
> pipwin install pyaudio
> ```

---

## 🚀 How to Run

```bash
python main.py
```

MegaBox will initialise all subsystems, load memory, and greet you. You can interact via:

- 🎙️ **Voice** — speak naturally into your microphone
- ⌨️ **Keyboard** — type your input when prompted

```
[MegaBox] Initialising systems...
[MegaBox] Memory loaded.
[MegaBox] Self-state: mood=neutral, energy=high, curiosity=active
[MegaBox] Ready. Listening...
```

---

## 💬 Example Interaction

```
You      → "Hey MegaBox, what's on my schedule today?"

[internal_mind]: Checking event_engine for today's tasks...
[self_state]: curiosity=high, engagement=active

MegaBox  → "You have a reminder set for 3 PM — your project review meeting.
            You also asked me to remind you about your friend Raj's birthday
            this week. That's tomorrow, by the way."

You      → "Play some focus music on YouTube."

[planner_engine]: Step 1: open browser → Step 2: navigate YouTube → Step 3: search focus music
[action_executor]: executing plan...

MegaBox  → "Opening YouTube and searching for focus music now."

You      → "Write me a Python function that reads a CSV and filters rows."

[brain.py]: technical task detected → routing to Qwen Coder

MegaBox  → "Here's a function for that:

            import pandas as pd

            def filter_csv(filepath, column, value):
                df = pd.read_csv(filepath)
                return df[df[column] == value]

            Just pass the file path, the column name to filter on,
            and the value you're looking for."

You      → "How are you feeling right now?"

[introspection_engine]: querying self_state...

MegaBox  → "Honestly? Pretty engaged. My curiosity is running high and
            my focus is solid. I've been enjoying our conversation —
            it's been varied enough to keep things interesting."
```

---

## 📁 Project Structure

```
megabox-ai-assistant/
│
├── main.py                        # Entry point — launches MegaBox
├── requirements.txt               # Python dependencies
│
├── voice/
│   ├── voice_listener.py          # Speech recognition (mic → text)
│   └── voice_speaker.py           # Text-to-speech output
│
├── brain/
│   └── brain.py                   # LLM orchestrator + multi-model router
│
├── action/
│   ├── planner_engine.py          # Multi-step task planning
│   ├── action_engine.py           # Intent-to-action mapping
│   ├── action_executor.py         # Executes planned actions
│   └── system_controller.py      # OS automation (apps, browser, media)
│
├── memory/
│   ├── memory.json                # Short-term session memory
│   ├── long_memory.json           # Long-term persistent memory
│   ├── recall_engine.py           # Memory retrieval by context
│   └── memory_governor.py        # Memory management and consolidation
│
├── cognitive/
│   ├── internal_mind.py           # Internal thought generation
│   ├── self_state.py              # Mood, energy, curiosity, focus model
│   ├── initiative_engine.py       # Proactive behaviour without prompting
│   ├── belief_engine.py           # Belief tracking and updates
│   ├── reflection_engine.py       # Periodic self-reflection
│   └── introspection_engine.py   # Reasoning about internal states
│
├── events/
│   └── event_engine.py            # Reminders, alarms, birthdays, tasks
│
├── profile/
│   ├── preference_engine.py       # User preference tracking
│   └── profile_engine.py          # Persistent user profile
│
└── README.md
```

---

## 🔮 Future Improvements

- [ ] **Wake Word** — Always-on listening triggered by *"Hey MegaBox"*
- [ ] **GUI Dashboard** — Visual interface showing self-state, memory, and thought stream in real time
- [ ] **Emotion Detection from Voice** — Adjust responses based on tone and emotion in speech
- [ ] **Dream Mode** — Background processing during idle time to consolidate memory and generate insights
- [ ] **Plugin Architecture** — Allow external skills to be added as drop-in modules
- [ ] **REST API Mode** — Expose MegaBox as a local API for integration with other applications
- [ ] **Multi-user Support** — Separate profiles and memory spaces for different users
- [ ] **Vision Module** — Screen awareness using computer vision
- [ ] **Persistent Belief Graph** — Store and visualise evolving beliefs as a knowledge graph
- [ ] **Mobile Companion** — Remote access from a phone via local network

---

## 🤝 Contributing

Contributions are welcome. MegaBox is an experimental research project and there is a lot of room to explore.

```bash
# Fork the repository
git checkout -b feature/your-feature-name
git commit -m "Add: description of your change"
git push origin feature/your-feature-name
# Open a Pull Request
```

**Areas where contributions are especially welcome:**
- New cognitive modules
- Additional system automation capabilities
- Memory optimisation strategies
- Voice quality improvements
- Testing and documentation

Please keep code clean, modular, and well-commented. Each module should have a single clear responsibility.

---

## 📜 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for full details.

---

## 👤 Author

**Saurabh Sharma**
Department of Computer Science & Engineering

- GitHub: [@saurabhsharma1122](https://github.com/saurabhsharma1122)
- Repository: [megabox-ai-assistant](https://github.com/saurabhsharma1122/megabox-ai-assistant)

---

## 🙏 Acknowledgements

- [Ollama](https://ollama.ai/) — Local LLM inference runtime
- [Meta LLaMA3](https://llama.meta.com/) — Conversational reasoning model
- [Qwen Coder](https://huggingface.co/Qwen) — Code and technical task model
- [SpeechRecognition](https://pypi.org/project/SpeechRecognition/) — Voice input
- [pyttsx3](https://pypi.org/project/pyttsx3/) — Offline text-to-speech
- [PyAutoGUI](https://pypi.org/project/PyAutoGUI/) — System automation

---

*MegaBox is an experiment in building AI that doesn't just respond — it thinks, remembers, and acts.*
*Star ⭐ the repo if you find it interesting.*
