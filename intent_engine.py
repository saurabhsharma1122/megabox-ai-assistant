from openai import OpenAI

client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")


def detect_intent(text):

    prompt = f"""
You are an intent classifier.

Classify the user's message into ONE of these intents:

play
open
close
search
volume
brightness
system
chat

Rules:
- If message implies action → choose action intent
- If message implies environment change → brightness
- If message implies sound → volume
- If message implies media → play
- If message implies opening anything → open
- If message implies closing anything → close
- If message implies looking for info → search
- Otherwise → chat

Return ONLY one word.

Message: "{text}"
Intent:
"""

    r = client.chat.completions.create(
        model="llama3",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=5
    )

    return r.choices[0].message.content.strip().lower()