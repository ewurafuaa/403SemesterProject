from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.template import Template

from utils import build_message, parse_message, reminder_text
from config import STUDENT_JID


class ReminderAgent(Agent):
    def __init__(self, jid, password):
        super().__init__(jid, password)
        self.last_sent = {}

    class SendReminderBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=2)
            if not msg:
                return

            if msg.get_metadata("msg_type") != "priority_update":
                return

            data = parse_message(msg)
            task_id = data["task_id"]
            title = data["title"]
            course = data["course"]
            priority = data["priority"]
            status = data["status"]
            time_remaining = data["time_remaining"]

            if status == "submitted":
                if self.agent.last_sent.get(task_id) != "submitted":
                    await self.send(build_message(
                        STUDENT_JID,
                        "inform",
                        "student_notice",
                        {
                            "text": f"Task '{title}' has been marked as completed. No further reminders will be sent."
                        }
                    ))
                    print(f"[ReminderAgent] Reminders stopped for task {task_id} because it has been completed.")
                    self.agent.last_sent[task_id] = "submitted"
                return

            # Avoid spamming the same reminder repeatedly
            previous_priority = self.agent.last_sent.get(task_id)

            if previous_priority != priority:
                text = reminder_text(title, course, priority, time_remaining)

                await self.send(build_message(
                    STUDENT_JID,
                    "inform",
                    "student_notice",
                    {"text": text}
                ))

                print(f"[ReminderAgent] Reminder sent: {priority.upper()} reminder delivered for task {task_id}.")
                self.agent.last_sent[task_id] = priority

    async def setup(self):
        print("[ReminderAgent] Started")
        template = Template()
        template.metadata = {"performative": "inform"}
        self.add_behaviour(self.SendReminderBehaviour(), template)