# memory_governor.py
"""
Cognitive update orchestrator.

Coordinates all memory subsystems after each user message.
Does NOT duplicate extraction logic — delegates to the specialist engines.

Main public API:
  cognitive_update(user_input)   → run all memory updates
  is_noisy(text)                 → True if input is too trivial to learn from
"""
import json
import os
import re
from datetime import datetime

SESSION_FILE = "session.json"
STATE_FILE   = "state.json"
GOALS_FILE   = "goals.json"

# Inputs with fewer words than this are unlikely to contain learnable facts
_MIN_WORDS = 3

# Patterns that are pure social filler — not worth processing
_NOISE_RE = re.compile(
    r"^(ok|okay|sure|fine|thanks|thank you|got it|alright|right|yep|"
    r"hello|hi|hey|bye|goodbye|no|yes|yeah|nah|nope|hmm|oh|ah|hm|"
    r"cool|nice|great|wow|really|seriously|interesting)[\s!?.]*$",
    re.IGNORECASE,
)


# -------------------------
# Storage helpers
# -------------------------

def _load(path: str, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        return default


def _save(path: str, data) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=4)


# -------------------------
# Noise detection
# -------------------------

def is_noisy(text: str) -> bool:
    """
    Return True if the input is too short or trivial to learn facts from.
    Used to skip expensive processing on filler messages.
    Session updates still run regardless — we want turn counts to be accurate.
    """
    stripped = text.strip()
    if len(stripped.split()) < _MIN_WORDS:
        return True
    if _NOISE_RE.match(stripped):
        return True
    return False


# -------------------------
# Session tracking
# -------------------------

def update_session(user_input: str) -> None:
    """Track last topic, timestamp, and turn count."""
    session = _load(SESSION_FILE, {
        "last_topic":     "",
        "last_timestamp": "",
        "turn_count":     0,
    })

    topic = re.sub(r"\s+", " ", user_input.strip())[:60]
    session["last_topic"]     = topic
    session["last_timestamp"] = datetime.now().isoformat()
    session["turn_count"]     = session.get("turn_count", 0) + 1

    _save(SESSION_FILE, session)


# -------------------------
# State clamping
# -------------------------

def stabilize_state() -> None:
    """Clamp all numeric state values to [0.0, 1.0]."""
    state = _load(STATE_FILE, {
        "curiosity":     0.5,
        "trust_in_user": 0.5,
        "confidence":    0.5,
        "mood":          "neutral",
        "assertiveness": 0.5,
    })

    for k in ["curiosity", "trust_in_user", "confidence", "assertiveness", "engagement", "energy"]:
        if k in state and isinstance(state[k], (int, float)):
            state[k] = round(max(0.0, min(1.0, state[k])), 4)

    _save(STATE_FILE, state)


# -------------------------
# Goal deduplication
# -------------------------

def clean_goals() -> None:
    """Remove duplicate goals, keep the 5 most recent."""
    goals = _load(GOALS_FILE, [])

    seen:   set  = set()
    unique: list = []
    for g in goals:
        if g not in seen:
            seen.add(g)
            unique.append(g)

    _save(GOALS_FILE, unique[-5:])


# -------------------------
# Master update
# -------------------------

def cognitive_update(user_input: str) -> None:
    """
    Run all memory subsystems after a user message.

    Session tracking runs on every turn (for accurate turn counts).
    All other updates are skipped for noisy/trivial inputs to avoid
    polluting memory with filler.
    """
    from profile_engine    import update_profile_from_input
    from preference_engine import update_preferences
    from belief_engine     import update_beliefs
    from reflection_engine import update_reflection

    # Always update session (turn count must be accurate)
    update_session(user_input)

    if is_noisy(user_input):
        return

    update_profile_from_input(user_input)
    update_preferences(user_input)
    update_beliefs(user_input)
    update_reflection(user_input)
    stabilize_state()
    clean_goals()