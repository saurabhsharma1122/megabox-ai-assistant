from openai import OpenAI

client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")


def plan_task(user_text):

    prompt = f"""
You are an autonomous AI planner.

User request:
"{user_text}"

Your job is to decide:

1) Is this a simple response?
OR
2) Does this require performing actions?

If it requires actions, output a step-by-step plan.

Rules:
- Do NOT explain
- Do NOT talk to user
- Only output JSON
- If no actions needed return:
{{"type":"chat"}}

If actions needed return:
{{
"type":"action",
"steps":[
"step1",
"step2"
]
}}
"""

    res = client.chat.completions.create(
        model="llama3",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=200
    )

    return res.choices[0].message.content.strip()