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

            data = parse_message(msg)
            if msg.get_metadata("msg_type") != "priority_update":
                return

            task_id = data["task_id"]
            priority = data["priority"]
            status = data["status"]

            if status == "submitted":
                if self.agent.last_sent.get(task_id) != "submitted":
                    await self.send(build_message(
                        STUDENT_JID,
                        "inform",
                        "student_notice",
                        {"text": f"Task '{data['title']}' completed. Reminders stopped."}
                    ))
                    self.agent.last_sent[task_id] = "submitted"
                return

            if self.agent.last_sent.get(task_id) != priority:
                text = reminder_text(
                    data["title"],
                    data["course"],
                    priority,
                    data["time_remaining"]
                )
                await self.send(build_message(
                    STUDENT_JID,
                    "inform",
                    "student_notice",
                    {"text": text}
                ))
                print(f"[ReminderAgent] Sent {priority} reminder for {task_id}")
                self.agent.last_sent[task_id] = priority

    async def setup(self):
        print("[ReminderAgent] Started")
        template = Template()
        template.metadata = {"performative": "inform"}
        self.add_behaviour(self.SendReminderBehaviour(), template)