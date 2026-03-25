import asyncio
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.template import Template

from models import Task
from utils import build_message, parse_message, compute_priority
from config import REMINDER_JID, TASK_JID


class PriorityAgent(Agent):
    class EvaluateBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=2)
            if not msg:
                return

            msg_type = msg.get_metadata("msg_type")
            data = parse_message(msg)

            if msg_type == "task_data":
                task = Task(**data)
                priority = compute_priority(task)
                print(f"[PriorityAgent] Decision made: '{task.title}' is classified as {priority.upper()} priority.")

                await self.send(build_message(
                    REMINDER_JID,
                    "inform",
                    "priority_update",
                    {
                        "task_id": task.task_id,
                        "title": task.title,
                        "course": task.course,
                        "priority": priority,
                        "status": task.status,
                        "time_remaining": task.time_remaining(),
                        "difficulty": task.difficulty
                    }
                ))

            elif msg_type == "all_tasks":
                tasks = data.get("tasks", [])
                for item in tasks:
                    task = Task(**item)
                    priority = compute_priority(task)

                    await self.send(build_message(
                        REMINDER_JID,
                        "inform",
                        "priority_update",
                        {
                            "task_id": task.task_id,
                            "title": task.title,
                            "course": task.course,
                            "priority": priority,
                            "status": task.status,
                            "time_remaining": task.time_remaining(),
                            "difficulty": task.difficulty
                        }
                    ))

    class MonitorTimeBehaviour(CyclicBehaviour):
        async def run(self):
            await self.send(build_message(
                TASK_JID,
                "inform",
                "request_all_tasks",
                {}
            ))
            await asyncio.sleep(5)

    async def setup(self):
        print("[PriorityAgent] Started")
        template = Template()
        template.metadata = {"performative": "inform"}
        self.add_behaviour(self.EvaluateBehaviour(), template)
        self.add_behaviour(self.MonitorTimeBehaviour())