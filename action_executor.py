import json
from system_controller import handle_system_command


def execute_plan(plan):

    try:
        data = json.loads(plan)
    except:
        return None

    if data["type"] == "chat":
        return None

    for step in data["steps"]:
        result = handle_system_command(step)

    return result