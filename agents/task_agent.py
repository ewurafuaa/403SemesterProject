from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.template import Template

from models import Task
from utils import build_message, parse_message
from config import PRIORITY_JID, STUDENT_JID


class TaskAgent(Agent):
    def __init__(self, jid, password):
        super().__init__(jid, password)
        self.tasks = {}

    class ManageTasksBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=2)
            if not msg:
                return

            msg_type = msg.get_metadata("msg_type")
            data = parse_message(msg)

            if msg_type == "add_task":
                task = Task(**data)
                self.agent.tasks[task.task_id] = task
                print(f"[TaskAgent] Task received and stored successfully: '{task.title}' for {task.course}.")

                await self.send(build_message(
                    PRIORITY_JID, "inform", "task_data", task.__dict__
                ))

            elif msg_type == "update_task_id":
                old_task_id = data["task_id"]
                new_task_id = data["new_task_id"]

                if old_task_id not in self.agent.tasks:
                    await self.send(build_message(
                        STUDENT_JID, "inform", "task_not_found", {"task_id": old_task_id}
                    ))
                    return

                if new_task_id in self.agent.tasks:
                    await self.send(build_message(
                        STUDENT_JID, "inform", "task_id_already_exists", {"task_id": new_task_id}
                    ))
                    return

                task = self.agent.tasks.pop(old_task_id)
                task.task_id = new_task_id
                self.agent.tasks[new_task_id] = task
                print(f"[TaskAgent] Task ID changed from {old_task_id} to {new_task_id}.")

                await self.send(build_message(
                    PRIORITY_JID, "inform", "task_data", task.__dict__
                ))

            elif msg_type == "update_title":
                task_id = data["task_id"]
                if task_id in self.agent.tasks:
                    self.agent.tasks[task_id].title = data["new_title"]
                    print(f"[TaskAgent] Title updated successfully for task {task_id}.")

                    await self.send(build_message(
                        PRIORITY_JID, "inform", "task_data", self.agent.tasks[task_id].__dict__
                    ))
                else:
                    await self.send(build_message(
                        STUDENT_JID, "inform", "task_not_found", {"task_id": task_id}
                    ))

            elif msg_type == "update_course":
                task_id = data["task_id"]
                if task_id in self.agent.tasks:
                    self.agent.tasks[task_id].course = data["new_course"]
                    print(f"[TaskAgent] Course code updated successfully for task {task_id}.")

                    await self.send(build_message(
                        PRIORITY_JID, "inform", "task_data", self.agent.tasks[task_id].__dict__
                    ))
                else:
                    await self.send(build_message(
                        STUDENT_JID, "inform", "task_not_found", {"task_id": task_id}
                    ))

            elif msg_type == "update_deadline":
                task_id = data["task_id"]
                if task_id in self.agent.tasks:
                    self.agent.tasks[task_id].due_ts = data["new_due_ts"]
                    print(f"[TaskAgent] Deadline updated successfully for task {task_id}.")

                    await self.send(build_message(
                        PRIORITY_JID, "inform", "task_data", self.agent.tasks[task_id].__dict__
                    ))
                else:
                    await self.send(build_message(
                        STUDENT_JID, "inform", "task_not_found", {"task_id": task_id}
                    ))

            elif msg_type == "update_difficulty":
                task_id = data["task_id"]
                if task_id in self.agent.tasks:
                    self.agent.tasks[task_id].difficulty = data["new_difficulty"]
                    print(f"[TaskAgent] Difficulty updated successfully for task {task_id}.")

                    await self.send(build_message(
                        PRIORITY_JID, "inform", "task_data", self.agent.tasks[task_id].__dict__
                    ))
                else:
                    await self.send(build_message(
                        STUDENT_JID, "inform", "task_not_found", {"task_id": task_id}
                    ))

            elif msg_type == "mark_done":
                task_id = data["task_id"]
                if task_id in self.agent.tasks:
                    self.agent.tasks[task_id].status = "submitted"
                    print(f"[TaskAgent] Task {task_id} has been marked as submitted.")

                    await self.send(build_message(
                        PRIORITY_JID, "inform", "task_data", self.agent.tasks[task_id].__dict__
                    ))
                else:
                    await self.send(build_message(
                        STUDENT_JID, "inform", "task_not_found", {"task_id": task_id}
                    ))

            elif msg_type == "request_all_tasks":
                all_tasks = [task.__dict__ for task in self.agent.tasks.values()]
                sender_jid = str(msg.sender).split("/")[0]

                response_type = "all_tasks_response"
                if "priority@" in sender_jid:
                    response_type = "all_tasks"

                await self.send(build_message(
                    sender_jid,
                    "inform",
                    response_type,
                    {"tasks": all_tasks}
                ))

            elif msg_type == "check_task_exists":
                task_id = data["task_id"]
                exists = task_id in self.agent.tasks

                await self.send(build_message(
                    STUDENT_JID,
                    "inform",
                    "check_task_exists_response",
                    {
                        "task_id": task_id,
                        "exists": exists
                    }
                ))

    async def setup(self):
        print("[TaskAgent] Started")
        template = Template()
        template.metadata = {"performative": "inform"}
        self.add_behaviour(self.ManageTasksBehaviour(), template)