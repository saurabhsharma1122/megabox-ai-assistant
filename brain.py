import json
import os
from event_engine import detect_event
from openai import OpenAI
from governor import decide_style
from system_controller import handle_system_command
from action_engine import handle_action
from planner_engine import plan_task
from action_executor import execute_plan
from confirmation_engine import get_pending, clear, is_confirmation, is_rejection
from internal_mind import recent_thoughts

# NEW IMPORTS
from recall_engine import build_recall_context
from profile_engine import get_profile_context
from preference_engine import get_preference_context
from belief_engine import get_belief_context


# -------------------------
# AI CLIENTS
# -------------------------
llama_client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
qwen_client  = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")


# -------------------------
# MODEL ROUTER
# -------------------------
def choose_model(user_input: str) -> str:
    t = user_input.lower()
    coding_keywords = [
        "code", "python", "program", "script",
        "algorithm", "debug", "function", "class", "coding"
    ]
    for word in coding_keywords:
        if word in t:
            return "qwen"
    return "llama"


# -------------------------
# SAFE LOAD
# -------------------------
def safe_load(path: str, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        return default


# -------------------------
# LOAD DATA
# -------------------------
def load_memory() -> list:
    return safe_load("memory.json", [])


def load_profile() -> dict:
    return safe_load("user_profile.json", {})


# -------------------------
# INTERNAL THOUGHT CONTEXT
# -------------------------
def build_thought_context(n: int = 4) -> str:

    thoughts = recent_thoughts(n)
    if not thoughts:
        return ""

    lines = [f"- {t['thought']}" for t in thoughts if t.get("thought")]
    if not lines:
        return ""

    block  = "Internal thoughts (not spoken — use only to guide your response):\n"
    block += "\n".join(lines) + "\n"
    return block


# -------------------------
# BUILD CONTEXT
# -------------------------
def build_context(user_input: str) -> str:

    memory = load_memory()
    recent = memory[-6:] if len(memory) > 6 else memory

    context = """You are Megabox, an autonomous AI assistant created by Saurabh.

Your identity:
- Your name is Megabox.
- You are a conversational AI assistant.
- You can perform tasks on the system and talk naturally.

Behavior rules:
Respond naturally.
Be concise.
Sound real.
Do not explain yourself.
Do not mention being an AI model.
Only speak what is necessary.
"""

    # -------------------------
    # PROFILE / PREFERENCE / BELIEF CONTEXT
    # -------------------------
    for builder in [get_profile_context, get_preference_context, get_belief_context]:
        try:
            block = builder()
            if block:
                context += f"\n{block}"
        except Exception:
            pass


    # -------------------------
    # RECALL ENGINE
    # -------------------------
    try:
        recall_block = build_recall_context(user_input)
        if recall_block:
            context += f"\n{recall_block}"
    except Exception:
        pass


    # -------------------------
    # INTERNAL THOUGHTS
    # -------------------------
    thought_context = build_thought_context(n=4)
    if thought_context:
        context += f"\n{thought_context}"


    # -------------------------
    # RECENT CONVERSATION
    # -------------------------
    context += "\nConversation:\n"

    for m in recent:
        context += f"User: {m['user']}\n"
        context += f"You: {m['agent']}\n"

    context += f"\nUser: {user_input}\nYou:"
    return context


# -------------------------
# MAIN RESPONSE
# -------------------------
def respond(user_input: str) -> str:

    # ===================================
    # EVENT DETECTION
    # ===================================
    try:
        event_reply = detect_event(user_input)
        if event_reply:
            return event_reply
    except Exception:
        pass


    # ===================================
    # CONFIRMATION SYSTEM
    # ===================================
    try:
        pending = get_pending()

        if pending:

            if is_confirmation(user_input):
                clear()

                if pending == "play_song":
                    from action_engine import generate_song_from_ai, play_song
                    song = generate_song_from_ai()
                    return play_song(song)

                clear()

            elif is_rejection(user_input):
                clear()

    except Exception:
        pass


    # ===================================
    # DIRECT ACTION ENGINE
    # ===================================
    try:
        action_result = handle_action(user_input)
        if action_result:
            return action_result
    except Exception:
        pass


    # ===================================
    # PLANNER ENGINE
    # ===================================
    try:
        plan = plan_task(user_input)
        if plan:
            result = execute_plan(plan)
            if result:
                return result
    except Exception:
        pass


    # ===================================
    # SYSTEM CONTROLLER
    # ===================================
    try:
        system_reply = handle_system_command(user_input)
        if system_reply:
            return system_reply
    except Exception:
        pass


    # ===================================
    # NORMAL AI CONVERSATION
    # ===================================
    style = decide_style(user_input)

    if not style["reply"]:
        return ""

    prompt = build_context(user_input)

    length_map = {
        "short":  60,
        "medium": 150,
        "long":   300
    }

    max_tokens = length_map.get(style["length"], 150)

    model_choice = choose_model(user_input)

    if model_choice == "qwen":
        model_name = "qwen2.5-coder:7b"
        client     = qwen_client
        max_tokens = 5000
    else:
        model_name = "llama3"
        client     = llama_client


    response = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.85,
        max_tokens=max_tokens
    )

    return response.choices[0].message.content.strip()
