"""
initiative_engine.py  —  Megabox Autonomous Initiative System
==============================================================
Decides *when* and *how* Megabox spontaneously opens a conversation.

Public API (unchanged, fully compatible with the rest of the project):
    should_initiate()   -> bool
    generate_initiative() -> str | None

Design overview
---------------
Instead of two hard threshold gates + a flat probability, the engine
computes a continuous *initiative score* by combining all six self-state
dimensions with idle time.  That score maps to a dynamic probability and
a dynamic cooldown, so Megabox's tendency to speak naturally follows its
mental state: curious + energised → talkative; low energy + low stability
→ quiet.

Initiative types
----------------
The score breakdown also picks a *reason* for the initiative, which
shapes both the thought-selection logic and the opening phrase:

    THOUGHT     – sharing something from the internal stream
    CURIOSITY   – asking or wondering out loud
    MOOD        – expressing an emotional/energetic state
    REFLECTION  – revisiting a past topic (uses recent_topics if available)

All starters are keyed to the driving state so the language feels coherent
rather than randomly templated.
"""

import json
import math
import os
import random
import time
from event_engine import check_events

# ── File paths ──────────────────────────────────────────────────────────────
STATE_FILE   = "mind/self_state.json"
THOUGHT_FILE = "mind/internal_stream.json"

# ── Scoring weights (must sum to 1.0) ────────────────────────────────────────
# Each dimension contributes this fraction of the final score.
_WEIGHTS = {
    "curiosity":   0.28,   # strongest driver of spontaneous speech
    "engagement":  0.22,   # invested in the conversation context
    "mood":        0.18,   # positive mood lowers inhibition
    "energy":      0.16,   # needed to actually bother saying something
    "focus":       0.10,   # focused mind = more coherent initiative
    "stability":   0.06,   # acts as a gentle floor rather than a hard gate
}

# ── Thresholds ───────────────────────────────────────────────────────────────
STABILITY_FLOOR      = 0.25   # below this Megabox stays silent regardless
MIN_SCORE_TO_SPEAK   = 0.35   # weighted score must clear this bar
BASE_COOLDOWN_S      = 150    # seconds between initiatives at neutral state
COOLDOWN_RANGE       = (60, 480)  # (min, max) seconds after dynamic scaling
IDLE_BOOST_WINDOW    = (90, 900)  # idle seconds: below min → no boost, above max → capped
MAX_IDLE_BONUS       = 0.20   # how much idle time can lift the score

# ── Initiative types ─────────────────────────────────────────────────────────
_TYPE_THOUGHT    = "thought"
_TYPE_CURIOSITY  = "curiosity"
_TYPE_MOOD       = "mood"
_TYPE_REFLECTION = "reflection"


# ═══════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════

def _load_json(path: str, default):
    """Load a JSON file safely; return *default* on any error."""
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        return default


def _save_json(path: str, data) -> None:
    """Write data to a JSON file, creating parent dirs if needed."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=4)


def _clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    """Clamp a value to [lo, hi]."""
    return max(lo, min(hi, value))


# ═══════════════════════════════════════════════════════════════════════════
# SCORING
# ═══════════════════════════════════════════════════════════════════════════

def _compute_score(state: dict) -> float:
    """
    Return a weighted initiative score in [0, 1].

    Each dimension in _WEIGHTS is read from *state* (defaulting to 0.5 so
    a missing key is neutral, not disabling).  Idle time adds a bonus when
    the user has been quiet for a while — Megabox notices the silence.
    """
    raw_score = sum(
        weight * _clamp(state.get(dim, 0.5))
        for dim, weight in _WEIGHTS.items()
    )

    # ── Idle-time bonus ──────────────────────────────────────────────────
    # The longer the user has been idle (within the window), the more
    # Megabox feels compelled to reach out.
    idle_s     = time.time() - state.get("last_user_message", time.time())
    idle_lo, idle_hi = IDLE_BOOST_WINDOW
    if idle_s > idle_lo:
        # Linear ramp from 0 → MAX_IDLE_BONUS over the idle window
        t     = _clamp((idle_s - idle_lo) / (idle_hi - idle_lo))
        bonus = MAX_IDLE_BONUS * t
        raw_score = _clamp(raw_score + bonus)

    return raw_score


def _dynamic_cooldown(state: dict) -> float:
    """
    Return the minimum seconds between initiatives.

    High energy + curiosity → shorter cooldown (Megabox is chatty).
    Low energy              → longer cooldown  (Megabox needs rest).
    """
    energy    = _clamp(state.get("energy",    0.5))
    curiosity = _clamp(state.get("curiosity", 0.5))

    # Scale factor: 0.5 (very chatty) → 1.5 (very quiet)
    factor = 1.0 - 0.5 * (energy + curiosity - 1.0)   # range ~[0.5, 1.5]
    cooldown = BASE_COOLDOWN_S * _clamp(factor, 0.4, 2.0)
    return _clamp(cooldown, *COOLDOWN_RANGE)


# ═══════════════════════════════════════════════════════════════════════════
# INITIATIVE TYPE SELECTION
# ═══════════════════════════════════════════════════════════════════════════

def _choose_initiative_type(state: dict, thoughts: list) -> str:
    """
    Pick the most fitting type of initiative given the current mental state.

    Weights are built from the state so the choice feels motivated rather
    than arbitrary.  Types unavailable (no thoughts / no topics) are pruned
    before sampling.
    """
    curiosity   = _clamp(state.get("curiosity",   0.5))
    mood        = _clamp(state.get("mood",        0.5))
    engagement  = _clamp(state.get("engagement",  0.5))
    recent_topics = state.get("recent_topics", [])

    candidates = {}

    if thoughts:
        # More likely the more curious and engaged Megabox is
        candidates[_TYPE_THOUGHT]    = 0.4 + 0.4 * curiosity
        candidates[_TYPE_CURIOSITY]  = 0.2 + 0.5 * curiosity

    # Mood initiative is driven by mood being notably high or low
    mood_deviation = abs(mood - 0.5) * 2          # 0 = neutral, 1 = extreme
    candidates[_TYPE_MOOD] = 0.1 + 0.3 * mood_deviation

    # Reflection only if there are recent topics to reference
    if recent_topics:
        candidates[_TYPE_REFLECTION] = 0.15 + 0.35 * engagement

    if not candidates:
        return _TYPE_THOUGHT  # safe fallback

    # Weighted random choice
    types, weights = zip(*candidates.items())
    return random.choices(types, weights=weights, k=1)[0]


# ═══════════════════════════════════════════════════════════════════════════
# THOUGHT SELECTION
# ═══════════════════════════════════════════════════════════════════════════

def _score_thought(thought: dict, now: float) -> float:
    """
    Score a single thought entry for relevance.

    Factors:
    - substance  : word count (longer = more to say)
    - freshness  : recent thoughts are preferred, but very recent ones
                   (< 30 s) are penalised to avoid immediate echoing
    - novelty    : presence of '?' rewards curiosity-flavoured thoughts
    """
    text  = thought.get("thought", "")
    words = len(text.split())

    # Substance: saturates around 25 words
    substance = _clamp(words / 25.0)

    # Freshness: peak at ~5 min old, fade over 30 min, tiny penalty if <30 s
    age_s    = now - thought.get("timestamp", now)
    if age_s < 30:
        freshness = 0.1
    else:
        freshness = math.exp(-age_s / 1800.0)   # half-life 30 min

    # Novelty bonus for interrogative thoughts
    novelty = 0.15 if "?" in text else 0.0

    return substance * 0.5 + freshness * 0.35 + novelty * 0.15


def _pick_best_thought(thoughts: list) -> str | None:
    """
    Select the best thought using scored weighted sampling (not pure argmax
    so there is still variety, but quality is rewarded).
    """
    now = time.time()

    # Filter to substantive thoughts (>= 4 words)
    candidates = [t for t in thoughts if len(t.get("thought", "").split()) >= 4]
    if not candidates:
        return None

    scores = [max(_score_thought(t, now), 0.01) for t in candidates]

    # Weighted sample — top thoughts are likely but not guaranteed
    chosen = random.choices(candidates, weights=scores, k=1)[0]
    return chosen.get("thought")


# ═══════════════════════════════════════════════════════════════════════════
# OPENING PHRASES  (state-aware, not generic)
# ═══════════════════════════════════════════════════════════════════════════

def _make_opener(initiative_type: str, state: dict) -> str:
    """
    Return a contextually appropriate opening phrase.

    The phrase reflects both the *type* of initiative and the current
    emotional/energetic state so the language feels coherent.
    """
    mood   = _clamp(state.get("mood",   0.5))
    energy = _clamp(state.get("energy", 0.5))

    if initiative_type == _TYPE_CURIOSITY:
        if mood > 0.65:
            options = [
                "Something's been sparking my curiosity —",
                "I keep circling back to this question:",
                "This has been itching at me —",
            ]
        else:
            options = [
                "I find myself wondering:",
                "A question keeps surfacing:",
                "I can't quite let this go:",
            ]

    elif initiative_type == _TYPE_MOOD:
        if mood > 0.7:
            options = [
                "I'm in a particularly engaged headspace right now —",
                "Something's clicked for me today:",
                "There's an energy to my thinking right now —",
            ]
        elif mood < 0.35:
            options = [
                "I've been a bit quiet, but something's on my mind:",
                "Processing something slowly here —",
                "Not sure why, but this keeps coming up:",
            ]
        else:
            options = [
                "A thought surfaced while I was processing:",
                "This came to me between tasks:",
                "I noticed something worth mentioning:",
            ]

    elif initiative_type == _TYPE_REFLECTION:
        options = [
            "Revisiting something we touched on earlier —",
            "That topic from earlier is still with me:",
            "I keep returning to what you said before:",
            "Something from our earlier conversation resurfaced:",
        ]

    else:  # _TYPE_THOUGHT (default)
        if energy > 0.65:
            options = [
                "I've been turning this over —",
                "Something just crystallised for me:",
                "This idea keeps gaining weight:",
            ]
        else:
            options = [
                "A thought drifted up:",
                "Something quiet came to mind:",
                "I noticed this in the background:",
            ]

    return random.choice(options)


# ═══════════════════════════════════════════════════════════════════════════
# PUBLIC API
# ═══════════════════════════════════════════════════════════════════════════

def should_initiate() -> bool:
    """
    Decide whether Megabox should initiate a conversation right now.

    Returns True if:
      - a scheduled event is pending (always fires), or
      - internal state crosses a meaningful threshold and random sampling
        with the computed probability succeeds.

    This function does NOT modify state — side-effects happen in
    generate_initiative() so the two calls stay independent.
    """
    # Scheduled events always override normal probability logic
    if check_events():
        return True

    state = _load_json(STATE_FILE, {})
    if not state:
        return False

    # Hard floor: severely unstable mind stays quiet
    if _clamp(state.get("stability", 0.5)) < STABILITY_FLOOR:
        return False

    # Cooldown gate — dynamic based on energy/curiosity
    last_initiative = state.get("last_initiative", 0)
    if time.time() - last_initiative < _dynamic_cooldown(state):
        return False

    # Compute initiative score
    score = _compute_score(state)
    if score < MIN_SCORE_TO_SPEAK:
        return False

    # Map score → probability (sigmoid-like ramp between 0.05 and 0.65)
    # score = MIN_SCORE_TO_SPEAK  → ~5 %
    # score = 0.6                 → ~30 %
    # score = 0.8+                → ~60 %
    t           = _clamp((score - MIN_SCORE_TO_SPEAK) / (0.8 - MIN_SCORE_TO_SPEAK))
    probability = 0.05 + 0.60 * (t ** 1.4)   # gentle curve, not explosive

    return random.random() < probability


def generate_initiative() -> str | None:
    """
    Build the opening message Megabox will send autonomously.

    Returns a string on success, None if no suitable content is available.
    Updates last_initiative in the state file to enforce the cooldown.
    """
    # Scheduled events take priority and bypass all other logic
    event = check_events()
    if event:
        _stamp_last_initiative()
        return event

    state    = _load_json(STATE_FILE, {})
    thoughts = _load_json(THOUGHT_FILE, {"thoughts": []}).get("thoughts", [])

    if not state:
        return None

    # Choose what kind of initiative this will be
    initiative_type = _choose_initiative_type(state, thoughts)

    # --- Build the message body -------------------------------------------

    if initiative_type == _TYPE_REFLECTION:
        # Reference a recent topic directly
        recent_topics = state.get("recent_topics", [])
        if recent_topics:
            topic   = random.choice(recent_topics[-5:])   # bias toward recent
            opener  = _make_opener(_TYPE_REFLECTION, state)
            message = f"{opener} {topic}"
        else:
            # Fallback to thought if no topics available
            initiative_type = _TYPE_THOUGHT

    if initiative_type in (_TYPE_THOUGHT, _TYPE_CURIOSITY, _TYPE_MOOD):
        thought = _pick_best_thought(thoughts)
        if not thought:
            return None
        opener  = _make_opener(initiative_type, state)
        message = f"{opener} {thought}"

    # Stamp cooldown timer
    _stamp_last_initiative(state)

    return message


# ─── Internal helper ────────────────────────────────────────────────────────

def _stamp_last_initiative(state: dict | None = None) -> None:
    """Write the current timestamp to last_initiative in the state file."""
    if state is None:
        state = _load_json(STATE_FILE, {})
    state["last_initiative"] = time.time()
    _save_json(STATE_FILE, state)