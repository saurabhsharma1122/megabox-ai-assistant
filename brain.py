import json
import os
from openai import OpenAI
from governor import decide_style
from system_controller import handle_system_command
from action_engine import handle_action
from planner_engine import plan_task
from action_executor import execute_plan


client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")


# -------------------------
# SAFE LOAD
# -------------------------
def safe_load(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r") as f:
            return json.load(f)
    except:
        return default


# -------------------------
# LOAD DATA
# -------------------------
def load_memory():
    return safe_load("memory.json", [])


def load_profile():
    return safe_load("user_profile.json", {})


# -------------------------
# BUILD CONTEXT
# -------------------------
def build_context(user_input):

    memory = load_memory()
    profile = load_profile()

    recent = memory[-6:] if len(memory) > 6 else memory
    name = profile.get("name", "")

    context = """
Respond naturally.
Be concise.
Sound real.
Do not explain yourself.
Do not mention being an AI.
Only speak what is necessary.
"""

    if name:
        context += f"\nUser name is {name}. Use naturally only if needed."

    context += "\nConversation:\n"

    for m in recent:
        context += f"User: {m['user']}\n"
        context += f"You: {m['agent']}\n"

    context += f"\nUser: {user_input}\nYou:"

    return context


# -------------------------
# MAIN RESPONSE
# -------------------------
def respond(user_input):

    # ===================================
    # 1️⃣ DIRECT ACTION ENGINE (fast commands)
    # ===================================
    try:
        action_result = handle_action(user_input)
        if action_result:
            return action_result
    except:
        pass


    # ===================================
    # 2️⃣ PLANNER ENGINE (complex reasoning)
    # ===================================
    try:
        plan = plan_task(user_input)

        if plan:
            result = execute_plan(plan)
            if result:
                return result
    except:
        pass


    # ===================================
    # 3️⃣ SYSTEM CONTROLLER (fallback)
    # ===================================
    try:
        system_reply = handle_system_command(user_input)
        if system_reply:
            return system_reply
    except:
        pass


    # ===================================
    # 4️⃣ NORMAL AI CONVERSATION
    # ===================================
    style = decide_style(user_input)

    if not style["reply"]:
        return ""

    prompt = build_context(user_input)

    length_map = {
        "short": 60,
        "medium": 150,
        "long": 300
    }

    max_tokens = length_map.get(style["length"], 150)

    response = client.chat.completions.create(
        model="llama3",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.85,
        max_tokens=max_tokens
    )

    return response.choices[0].message.content.strip()