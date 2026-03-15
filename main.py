import os
import sys
import time
import threading
import re

from internal_mind import think
from trait_engine import evolve_traits
from memory_governor import cognitive_update
from brain import respond
from profile_engine import update_profile_from_input
from reflection_engine import update_reflection
from introspection_engine import update_internal_thoughts
from belief_engine import update_beliefs
from self_reflection_engine import reflect
from preference_engine import update_preferences
from recall_engine import search_memory
from self_awareness import evaluate_state
from initiative_engine import should_initiate, generate_initiative

# VOICE MODULES
from voice_listener import listen
from voice_speaker import speak


IDLE_THRESHOLD = 600
last_interaction_time = time.time()
running = True

# wake words
WAKE_WORDS = ["mega box", "megabox", "hey megabox", "hey mega box"]


# -------------------------
# CODE DETECTION
# -------------------------
def is_code(text):

    code_patterns = [
        r"def ",
        r"class ",
        r"import ",
        r"print\(",
        r"for ",
        r"while ",
        r"if __name__",
        r"{",
        r"}",
        r";"
    ]

    for pattern in code_patterns:
        if re.search(pattern, text):
            return True

    return False


# -------------------------
# IDLE MONITOR THREAD
# -------------------------
def idle_monitor():
    global last_interaction_time
    global running

    idle_spoken = False

    while running:
        time.sleep(5)

        if time.time() - last_interaction_time > IDLE_THRESHOLD and not idle_spoken:

            if should_initiate():
                msg = generate_initiative()

                if msg:
                    print("\nmegabox:", msg)

                    if not is_code(msg):
                        speak(msg)

                    reflect("", msg)

            idle_spoken = True

        if time.time() - last_interaction_time <= 2:
            idle_spoken = False


# -------------------------
# VOICE LISTENER THREAD
# -------------------------
def voice_loop():
    global last_interaction_time
    global running

    while running:

        heard = listen()

        if not heard:
            continue

        heard = heard.strip()

        # ignore very short noise
        if len(heard) < 2:
            continue

        # wake word detection
        if heard.lower() in WAKE_WORDS:
            print("\nmegabox: Yes?")
            speak("Yes?")
            continue

        last_interaction_time = time.time()

        print("\nYou (voice):", heard)

        try:

            # cognition BEFORE reply
            update_profile_from_input(heard)
            update_reflection(heard)
            update_internal_thoughts(heard)
            update_beliefs(heard)
            cognitive_update(heard)
            update_preferences(heard)
            evolve_traits(heard)

            reply = respond(heard)

            if reply:
                print("megabox:", reply)

                # do not speak code
                if not is_code(reply):
                    speak(reply)

                # cognition AFTER reply
                reflect(heard, reply)
                evaluate_state(heard, reply)
                think(heard)

        except Exception as e:
            print("Voice processing error:", e)


# -------------------------
# SET WORKING DIRECTORY
# -------------------------
os.chdir(os.path.dirname(os.path.abspath(__file__)))
print("megabox initialized.")


# start background threads
threading.Thread(target=idle_monitor, daemon=True).start()
threading.Thread(target=voice_loop, daemon=True).start()


# -------------------------
# MAIN TEXT LOOP
# -------------------------
try:
    while True:

        user_input = input("You: ").strip()

        if not user_input:
            continue

        if user_input.lower() == "exit":
            running = False
            print("megabox: Shutting down.")
            break

        # ignore wake words in text mode
        if user_input.lower() in WAKE_WORDS:
            print("megabox: Yes?")
            continue

        last_interaction_time = time.time()

        try:

            # cognition BEFORE reply
            update_profile_from_input(user_input)
            update_reflection(user_input)
            update_internal_thoughts(user_input)
            update_beliefs(user_input)
            cognitive_update(user_input)
            update_preferences(user_input)
            evolve_traits(user_input)

            reply = respond(user_input)

            if reply:
                print("megabox:", reply)

                # do not speak code
                if not is_code(reply):
                    speak(reply)

                # cognition AFTER reply
                reflect(user_input, reply)
                evaluate_state(user_input, reply)
                think(user_input)

        except Exception as e:
            print("Processing error:", e)


except KeyboardInterrupt:
    running = False
    print("\nmegabox: Interrupted. Shutting down cleanly.")
    sys.exit(0)
