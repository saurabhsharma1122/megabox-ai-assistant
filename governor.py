import random
import json
import os

STATE_FILE = "state.json"
PROFILE_FILE = "user_profile.json"


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
# GET INTERNAL STATE
# -------------------------
def get_state():
    return safe_load(STATE_FILE, {
        "curiosity": 0.6,
        "mood": "neutral",
        "confidence": 0.5,
        "interest": 0.5
    })


# -------------------------
# GET USER PROFILE
# -------------------------
def get_profile():
    return safe_load(PROFILE_FILE, {})


# -------------------------
# ANALYZE USER INPUT
# -------------------------
def analyze_input(user_input):

    text = user_input.strip().lower()

    if not text:
        return "empty"

    if len(text) <= 2:
        return "minimal"

    if len(text.split()) == 1:
        return "single_word"

    if "?" in text:
        return "question"

    if len(text) < 25:
        return "short"

    return "normal"


# -------------------------
# DECIDE RESPONSE STYLE
# -------------------------
def decide_style(user_input):

    state = get_state()
    profile = get_profile()
    intent = analyze_input(user_input)

    curiosity = state.get("curiosity", 0.6)
    confidence = state.get("confidence", 0.5)
    interest = state.get("interest", 0.5)

    style = {
        "reply": True,
        "length": "medium",
        "tone": "neutral",
        "curious": False
    }

    # -------------------------
    # SILENCE LOGIC
    # -------------------------
    if intent == "empty":
        style["reply"] = False
        return style

    if intent == "minimal":
        style["length"] = "short"

    if intent == "single_word":
        style["length"] = "short"

    if intent == "question":
        style["length"] = "medium"

    if intent == "short":
        style["length"] = "short"

    # -------------------------
    # CURIOSITY TRIGGER
    # -------------------------
    if curiosity > 0.7 and random.random() < curiosity:
        style["curious"] = True

    # -------------------------
    # CONFIDENCE TONE
    # -------------------------
    if confidence > 0.7:
        style["tone"] = "assertive"

    if confidence < 0.3:
        style["tone"] = "uncertain"

    # -------------------------
    # INTEREST CONTROL
    # -------------------------
    if interest < 0.3:
        style["length"] = "short"

    if interest > 0.75:
        style["length"] = "long"

    return style