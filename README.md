MegaBox – Local AI Voice Assistant

MegaBox is a local AI assistant built in Python that combines:

- Conversational intelligence (LLM powered)
- Voice interaction
- System automation
- Task execution on the computer

The assistant can talk, think, remember context, and perform actions on the system.

---

Features

Conversational AI

- Uses local LLM via Ollama
- Maintains conversation context
- Natural dialogue responses

Voice Interaction

- Speech recognition (microphone input)
- Text-to-speech voice output
- Works with both voice and keyboard input

Memory System

- Stores conversation history
- User profile tracking
- Internal thought stream simulation

System Automation

MegaBox can control parts of the system:

- Open applications
- Control browser
- Play songs
- Play YouTube videos
- Search the internet
- Close programs
- Control brightness
- Switch windows
- Close tabs

Planning Engine

Complex requests are handled using a task planner that breaks requests into steps before executing actions.

---

Project Architecture

![WhatsApp Image 2026-03-12 at 5 52 28 PM](https://github.com/user-attachments/assets/b4e3e69c-3a2a-45a5-8ae6-43298b50a793)


---

Installation

Clone the repository:

git clone https://github.com/YOUR_USERNAME/megabox-ai-assistant.git
cd megabox-ai-assistant

Install dependencies:

pip install -r requirements.txt

Make sure Ollama is installed and running locally.

---

Running the Assistant

Run the assistant with:

python main.py

The assistant supports:

- voice input
- keyboard input

---

Example Commands

Examples of tasks MegaBox can perform:

play believer
play a song
open youtube
play funny video on youtube
close chrome
search artificial intelligence

---

Technologies Used

- Python
- Ollama (Local LLM)
- SpeechRecognition
- pyttsx3
- PyAutoGUI
- Requests

---

Project Status
<img width="1919" height="661" alt="image" src="https://github.com/user-attachments/assets/c1f9c315-1d6b-467b-b4e6-aeaf0534c2e7" />


This project is an experimental AI assistant prototype exploring:

- autonomous behavior
- task planning
- human-AI interaction

More improvements and capabilities will be added in future updates.

---

License

MIT License
