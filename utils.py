import json
from spade.message import Message


def build_message(to, performative, msg_type, payload):
    msg = Message(to=to)
    msg.set_metadata("performative", performative)
    msg.set_metadata("msg_type", msg_type)
    msg.body = json.dumps(payload)
    return msg


def parse_message(msg):
    return json.loads(msg.body) if msg.body else {}


def format_time_remaining(seconds):
    if seconds <= 0:
        return "0 minutes"

    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)

    parts = []
    if days > 0:
        parts.append(f"{days} day{'s' if days != 1 else ''}")
    if hours > 0:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if minutes > 0:
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")

    if not parts:
        return "less than a minute"

    if len(parts) == 1:
        return parts[0]
    if len(parts) == 2:
        return f"{parts[0]} and {parts[1]}"
    return f"{parts[0]}, {parts[1]}, and {parts[2]}"


def compute_priority(task):
    remaining = task.time_remaining()
    difficulty = task.difficulty.strip().lower()

    SIX_HOURS = 6 * 60 * 60
    TWENTY_FOUR_HOURS = 24 * 60 * 60
    SEVEN_DAYS = 7 * 24 * 60 * 60

    if task.status == "submitted":
        return "none"

    if remaining <= 0:
        return "overdue"

    if remaining <= SIX_HOURS:
        return "urgent"

    if remaining <= TWENTY_FOUR_HOURS:
        return "high"

    if remaining <= SEVEN_DAYS:
        return "medium"

    if difficulty == "high":
        return "medium"

    return "low"


def reminder_text(title, course, priority, seconds_left):
    remaining_text = format_time_remaining(seconds_left)

    if priority == "urgent":
        return (
            f"URGENT REMINDER: '{title}' for {course} is due in {remaining_text}. "
            f"Please give it immediate attention."
        )

    if priority == "high":
        return (
            f"HIGH PRIORITY REMINDER: '{title}' for {course} is due in {remaining_text}. "
            f"You should work on it soon."
        )

    if priority == "medium":
        return (
            f"GENTLE REMINDER: '{title}' for {course} is due in {remaining_text}. "
            f"It is being monitored by the system."
        )

    if priority == "low":
        return (
            f"NOTICE: '{title}' for {course} is scheduled and currently has low urgency."
        )

    if priority == "overdue":
        return (
            f"OVERDUE ALERT: '{title}' for {course} has passed its deadline."
        )

    return f"'{title}' is being monitored."