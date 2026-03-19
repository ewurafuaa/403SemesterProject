import json
import time
from spade.message import Message


def build_message(to, performative, msg_type, payload):
    msg = Message(to=to)
    msg.set_metadata("performative", performative)
    msg.set_metadata("msg_type", msg_type)
    msg.body = json.dumps(payload)
    return msg


def parse_message(msg):
    return json.loads(msg.body) if msg.body else {}


def compute_priority(task):
    remaining = task.time_remaining()
    difficulty = task.difficulty.strip().lower()

    # Time thresholds in seconds
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

    # Difficulty can slightly increase priority for distant tasks
    if difficulty == "high":
        return "medium"

    return "low"


def reminder_text(title, course, priority, seconds_left):
    if priority == "urgent":
        return f"URGENT: {title} for {course} is due in {seconds_left:.0f} seconds."
    if priority == "high":
        return f"Reminder: {title} for {course} is due soon."
    if priority == "medium":
        return f"Gentle reminder: {title} for {course} is coming up."
    if priority == "overdue":
        return f"OVERDUE: {title} for {course} has passed its deadline."
    return f"{title} is being monitored."