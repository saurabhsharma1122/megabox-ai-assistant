def evaluate_emotional_state(state, user_input):
    lower = user_input.lower()

    # Emotional intensity triggers
    if any(word in lower for word in ["sad", "tired", "confused", "lost"]):
        state["emotional_intensity"] = min(1, state.get("emotional_intensity", 0.4) + 0.1)

    # Assertiveness trigger
    if any(word in lower for word in ["prove", "wrong", "argue", "debate"]):
        state["assertiveness"] = min(1, state.get("assertiveness", 0.6) + 0.1)

    # Curiosity trigger
    if "?" in user_input:
        state["curiosity"] = min(1, state.get("curiosity", 0.7) + 0.05)

    return state
