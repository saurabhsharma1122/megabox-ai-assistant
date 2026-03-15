import json
import os
import re
import time
from datetime import datetime, timedelta

EVENT_FILE = "mind/events.json"

# ---------------------------------------------------------------
# Event type registry
# ---------------------------------------------------------------
EVENT_TYPES = {
    "reminder":    "reminder",
    "birthday":    "birthday",
    "alarm":       "alarm",
    "task":        "task",
    "anniversary": "anniversary",
}

# ---------------------------------------------------------------
# Storage
# ---------------------------------------------------------------

def load_events() -> dict:
    if not os.path.exists(EVENT_FILE):
        return {"events": []}
    try:
        with open(EVENT_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {"events": []}


def save_events(data: dict) -> None:
    os.makedirs(os.path.dirname(EVENT_FILE), exist_ok=True)
    with open(EVENT_FILE, "w") as f:
        json.dump(data, f, indent=4)


def add_event(
    event_type: str,
    trigger_time: float,
    message: str,
    label: str = ""
) -> None:
    events = load_events()
    events["events"].append({
        "type":       event_type,
        "time":       trigger_time,
        "message":    message,
        "label":      label,
        "triggered":  False,
        "created_at": time.time(),
    })
    save_events(events)


def delete_event(label: str) -> bool:
    """Remove all events whose label matches. Returns True if any were removed."""
    events = load_events()
    before = len(events["events"])
    events["events"] = [
        e for e in events["events"]
        if e.get("label", "").lower() != label.lower()
    ]
    if len(events["events"]) < before:
        save_events(events)
        return True
    return False


def list_pending() -> list:
    """Return all events that have not yet triggered."""
    events = load_events()
    now = time.time()
    return [
        e for e in events["events"]
        if not e["triggered"] and e["time"] > now
    ]


# ---------------------------------------------------------------
# Time parsing helpers
# ---------------------------------------------------------------

def _offset_from_now(seconds: float) -> float:
    return time.time() + seconds


def _parse_offset(text: str):
    """
    Parse relative and absolute time expressions.
    Returns a Unix timestamp or None if no time expression was found.

    Supports:
        in N minutes / hours / days / weeks
        tomorrow
        next week / next month
        at HH:MM am/pm  (today, or tomorrow if the time has already passed)
        on <weekday>    (next occurrence of that day)
    """
    t = text.lower().strip()

    # in N minutes / hours / days / weeks
    m = re.search(r"in\s+(\d+)\s+(minute|hour|day|week)s?", t)
    if m:
        n = int(m.group(1))
        unit = m.group(2)
        multipliers = {"minute": 60, "hour": 3600, "day": 86400, "week": 604800}
        return _offset_from_now(n * multipliers[unit])

    if "tomorrow" in t:
        return _offset_from_now(86400)

    if "next week" in t:
        return _offset_from_now(7 * 86400)

    if "next month" in t:
        return _offset_from_now(30 * 86400)

    # at HH:MM or HH am/pm
    m = re.search(r"at\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", t)
    if m:
        hour   = int(m.group(1))
        minute = int(m.group(2)) if m.group(2) else 0
        period = m.group(3)
        if period == "pm" and hour != 12:
            hour += 12
        elif period == "am" and hour == 12:
            hour = 0
        now = datetime.now()
        target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if target <= now:
            target += timedelta(days=1)
        return target.timestamp()

    # on <weekday>
    weekdays = ["monday", "tuesday", "wednesday", "thursday",
                "friday", "saturday", "sunday"]
    for i, day in enumerate(weekdays):
        if day in t:
            now = datetime.now()
            days_ahead = (i - now.weekday()) % 7
            if days_ahead == 0:
                days_ahead = 7
            target = now + timedelta(days=days_ahead)
            target = target.replace(hour=9, minute=0, second=0, microsecond=0)
            return target.timestamp()

    return None


def _format_trigger_time(ts: float) -> str:
    """Return a natural-language description of a Unix timestamp."""
    dt  = datetime.fromtimestamp(ts)
    now = datetime.now()
    delta = dt - now

    if delta.days == 0:
        return f"today at {dt.strftime('%I:%M %p')}"
    elif delta.days == 1:
        return "tomorrow"
    elif delta.days < 7:
        return f"on {dt.strftime('%A')}"
    else:
        return dt.strftime("%B %d at %I:%M %p")


# ---------------------------------------------------------------
# Pattern handlers
# ---------------------------------------------------------------

def _try_cancel(t: str, original: str):
    if not re.search(r"\b(cancel|delete|remove)\b.*(reminder|alarm|event)", t):
        return None

    label_raw = re.sub(
        r"(cancel|delete|remove)\s+(my\s+)?(reminder|alarm|event)\s*(for|about)?",
        "", t
    ).strip()

    if label_raw and delete_event(label_raw):
        return f"Done. I removed the reminder for '{label_raw}'."
    return "I couldn't find a matching reminder to remove."


def _try_list_events(t: str, original: str):
    if not re.search(
        r"\b(what reminders|list.*(reminder|event|alarm)|upcoming events|my reminders)\b", t
    ):
        return None

    pending = list_pending()
    if not pending:
        return "You have no upcoming reminders or events."

    lines = []
    for e in sorted(pending, key=lambda x: x["time"])[:8]:
        when  = _format_trigger_time(e["time"])
        label = e.get("label") or e.get("message", "")
        lines.append(f"• {label.capitalize()} — {when}")

    return "Here are your upcoming events:\n" + "\n".join(lines)


def _try_alarm(t: str, original: str):
    if not re.search(r"\b(alarm|wake me)\b", t):
        return None

    ts = _parse_offset(t)
    if not ts:
        return "I understood you want an alarm, but couldn't parse the time. Try 'set an alarm at 7am'."

    add_event("alarm", ts, f"Alarm: {_format_trigger_time(ts).capitalize()}!", label="alarm")
    return f"Alarm set for {_format_trigger_time(ts)}."


def _extract_birthday_name(t: str):
    """
    Extract who the birthday belongs to from a birthday phrase.

    Returns a tuple of (display_name, label_name, is_self).

    Examples:
        "my birthday is tomorrow"       → ("yours", "my birthday", True)
        "john's birthday is next week"  → ("John's", "john birthday", False)
        "it's mom's birthday tomorrow"  → ("Mom's", "mom birthday", False)
        "birthday tomorrow"             → ("Someone's", "birthday", False)
    """
    # First-person: "my birthday"
    if re.search(r"\bmy\s+birthday\b", t):
        return ("yours", "my birthday", True)

    # Third-person possessive: "john's birthday", "mom's birthday"
    # Explicitly exclude the word "birthday" itself from being captured as a name
    name_match = re.search(r"\b([a-z]+)'s\s+birthday\b", t)
    if name_match:
        raw = name_match.group(1)
        if raw != "birthday":
            name = raw.capitalize()
            return (f"{name}'s", f"{raw} birthday", False)

    # Non-possessive: "john birthday tomorrow", "birthday for mom"
    for_match = re.search(r"birthday\s+(?:for|of)\s+([a-z]+)", t)
    if for_match:
        raw = for_match.group(1)
        name = raw.capitalize()
        return (f"{name}'s", f"{raw} birthday", False)

    return ("Someone's", "birthday", False)


def _try_birthday(t: str, original: str):
    if "birthday" not in t:
        return None

    # Default to 1 year for birthdays with no explicit time (annual event)
    ts = _parse_offset(t) or _offset_from_now(365 * 86400)

    display_name, label, is_self = _extract_birthday_name(t)

    if is_self:
        message = "Today is your birthday! Happy Birthday!"
        confirm = f"Got it. I'll remember your birthday ({_format_trigger_time(ts)})."
    else:
        message = f"Today is {display_name} birthday!"
        confirm = f"Got it. I'll remember {display_name} birthday ({_format_trigger_time(ts)})."

    add_event("birthday", ts, message, label=label)
    return confirm


def _try_anniversary(t: str, original: str):
    if "anniversary" not in t:
        return None

    ts = _parse_offset(t) or _offset_from_now(86400)
    add_event("anniversary", ts, "Anniversary reminder!", label="anniversary")
    return f"Anniversary noted for {_format_trigger_time(ts)}."


def _try_task(t: str, original: str):
    if not re.search(r"\b(don'?t forget|remember to|make sure)\b", t):
        return None

    ts = _parse_offset(t) or _offset_from_now(3600)

    label_raw = re.sub(r"don'?t forget|remember to|make sure", "", t).strip()
    label_raw = re.sub(
        r"(in \d+ \w+|tomorrow|next week|at \d+(?::\d+)?(?:\s*[ap]m)?)",
        "", label_raw
    ).strip(" to,")
    label = label_raw if label_raw else "task"

    add_event("task", ts, f"Don't forget: {label.capitalize()}.", label=label)
    return f"Noted. I'll remind you about '{label}' {_format_trigger_time(ts)}."


def _try_reminder(t: str, original: str):
    if "remind me" not in t:
        return None

    ts = _parse_offset(t)
    if not ts:
        return (
            "I understood you want a reminder, but couldn't figure out when. "
            "Try something like 'remind me in 2 hours'."
        )

    label_raw = re.sub(
        r"remind me (in \d+ \w+|tomorrow|next week|next month"
        r"|at \d+(?::\d+)?(?:\s*[ap]m)?|on \w+day)",
        "", t
    ).strip(" to about,")
    label   = label_raw if label_raw else "reminder"
    message = (
        f"Reminder: {label.capitalize()}."
        if label != "reminder"
        else "You asked me to remind you."
    )

    add_event("reminder", ts, message, label=label)
    return f"Got it. I'll remind you {_format_trigger_time(ts)}."


# ---------------------------------------------------------------
# Ordered handler list — first match wins
# ---------------------------------------------------------------
_PATTERNS = [
    _try_cancel,
    _try_list_events,
    _try_alarm,
    _try_birthday,
    _try_anniversary,
    _try_task,
    _try_reminder,    # most general — always last
]


# ---------------------------------------------------------------
# Public API
# ---------------------------------------------------------------

def detect_event(text: str):
    """
    Scan user input for any schedulable event or reminder intent.
    Returns a confirmation string if an event was stored, otherwise None.
    Called by brain.py before the AI conversation stage.
    """
    t = text.lower()

    for handler in _PATTERNS:
        try:
            result = handler(t, text)
            if result:
                return result
        except Exception:
            continue

    return None


def check_events():
    """
    Check whether any stored event has reached its trigger time.
    Mark it as triggered and return its message.
    Call this regularly from the main loop (e.g. every 30 seconds).
    Fires one event per call to avoid flooding.
    """
    events = load_events()
    now    = time.time()
    fired_message = None

    for event in events["events"]:
        if not event["triggered"] and now >= event["time"]:
            event["triggered"] = True
            fired_message = event["message"]
            break

    if fired_message:
        save_events(events)

    return fired_message