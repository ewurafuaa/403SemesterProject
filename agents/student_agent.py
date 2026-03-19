import asyncio
import time
from datetime import datetime
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.template import Template

from utils import build_message, parse_message
from config import TASK_JID


def format_time_remaining(seconds):
    if seconds <= 0:
        return "The due date has already passed."

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


class StudentAgent(Agent):
    def __init__(self, jid, password):
        super().__init__(jid, password)
        self.pending_responses = {}

    class ReceiveBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=2)
            if msg:
                data = parse_message(msg)
                msg_type = msg.get_metadata("msg_type")

                if msg_type in {
                    "check_task_exists_response",
                    "all_tasks_response",
                    "task_updated",
                    "task_not_found",
                    "task_id_already_exists"
                }:
                    self.agent.pending_responses[msg_type] = data
                    return

                print(f"\n[StudentAgent] Notification received: {data.get('text', '')}")

    class InteractiveMenuBehaviour(CyclicBehaviour):
        async def get_non_empty_input(self, prompt):
            while True:
                value = await asyncio.to_thread(input, prompt)
                value = value.strip()
                if value:
                    return value
                print("\n[StudentAgent] Invalid input. This field cannot be empty. Please try again.\n")

        async def get_valid_main_menu_choice(self):
            while True:
                choice = await asyncio.to_thread(input, "Enter your choice (1-4): ")
                choice = choice.strip()
                if choice in {"1", "2", "3", "4"}:
                    return choice
                print("\n[StudentAgent] Invalid choice. Please enter a number from 1 to 4.\n")

        async def get_valid_edit_menu_choice(self):
            while True:
                choice = await asyncio.to_thread(input, "Enter your choice (1-6): ")
                choice = choice.strip()
                if choice in {"1", "2", "3", "4", "5", "6"}:
                    return choice
                print("\n[StudentAgent] Invalid choice. Please enter a number from 1 to 6.\n")

        async def get_valid_datetime(self, prompt):
            while True:
                due_date = await asyncio.to_thread(input, prompt)
                due_date = due_date.strip()

                try:
                    due_datetime = datetime.strptime(due_date, "%Y-%m-%d %H:%M")
                    due_ts = due_datetime.timestamp()
                    remaining = due_ts - time.time()

                    if remaining <= 0:
                        print("\n[StudentAgent] Invalid input. The due date must be in the future. Please try again.\n")
                        continue

                    return due_datetime, due_ts, remaining

                except ValueError:
                    print("\n[StudentAgent] Invalid date format. Please use YYYY-MM-DD HH:MM.\n")

        async def get_valid_difficulty(self):
            while True:
                difficulty = await asyncio.to_thread(
                    input,
                    "Enter difficulty (L = Low, M = Medium, H = High): "
                )
                difficulty = difficulty.strip().lower()

                if difficulty in ["l", "low"]:
                    return "low"
                elif difficulty in ["m", "medium"]:
                    return "medium"
                elif difficulty in ["h", "high"]:
                    return "high"
                else:
                    print("\n[StudentAgent] Invalid input. Please enter L, M, H or low, medium, high.\n")

        async def wait_for_response(self, response_type, timeout=5):
            waited = 0
            while waited < timeout:
                if response_type in self.agent.pending_responses:
                    return self.agent.pending_responses.pop(response_type)
                await asyncio.sleep(0.2)
                waited += 0.2
            return None

        async def show_available_tasks(self):
            await self.send(build_message(
                TASK_JID,
                "inform",
                "request_all_tasks",
                {}
            ))

            response = await self.wait_for_response("all_tasks_response")

            if not response:
                print("\n[StudentAgent] Could not retrieve tasks at the moment.\n")
                return

            tasks = response.get("tasks", [])
            if not tasks:
                print("\n[StudentAgent] There are currently no tasks in the system.\n")
                return

            print("\n================ AVAILABLE TASKS ================")
            for task in tasks:
                due_dt = datetime.fromtimestamp(task["due_ts"]).strftime("%d %B %Y at %I:%M %p")
                print(
                    f"Task ID: {task['task_id']} | "
                    f"Title: {task['title']} | "
                    f"Course: {task['course']} | "
                    f"Difficulty: {task['difficulty']} | "
                    f"Status: {task['status']} | "
                    f"Due: {due_dt}"
                )
            print("=================================================\n")

        async def prompt_for_existing_task_id(self, action_name):
            while True:
                task_id = await self.get_non_empty_input(f"Enter task ID to {action_name}: ")

                await self.send(build_message(
                    TASK_JID,
                    "inform",
                    "check_task_exists",
                    {"task_id": task_id}
                ))

                response = await self.wait_for_response("check_task_exists_response")

                if response and response.get("exists"):
                    return task_id

                print(f"\n[StudentAgent] No task with ID '{task_id}' exists in the system.")
                print("What would you like to do next?")
                print("1. View available tasks")
                print("2. Retry with another task ID\n")

                while True:
                    option = await asyncio.to_thread(input, "Enter your choice (1-2): ")
                    option = option.strip()

                    if option == "1":
                        await self.show_available_tasks()
                        break
                    elif option == "2":
                        break
                    else:
                        print("\n[StudentAgent] Invalid choice. Please enter 1 or 2.\n")

        async def prompt_for_new_unique_task_id(self):
            while True:
                new_task_id = await self.get_non_empty_input("Enter the new task ID: ")

                await self.send(build_message(
                    TASK_JID,
                    "inform",
                    "check_task_exists",
                    {"task_id": new_task_id}
                ))

                response = await self.wait_for_response("check_task_exists_response")

                if response and not response.get("exists"):
                    return new_task_id

                print(f"\n[StudentAgent] Task ID '{new_task_id}' already exists. Please enter a different one.\n")

        async def add_task_flow(self):
            task_id = await self.get_non_empty_input("Enter task ID (e.g. T1): ")
            title = await self.get_non_empty_input("Enter task title: ")
            course = await self.get_non_empty_input("Enter course code: ")
            due_datetime, due_ts, remaining = await self.get_valid_datetime(
                "Enter due date and time (YYYY-MM-DD HH:MM): "
            )
            difficulty = await self.get_valid_difficulty()

            readable_remaining = format_time_remaining(remaining)
            formatted_due = due_datetime.strftime("%d %B %Y at %I:%M %p")

            print(f"[StudentAgent] Difficulty recorded as: {difficulty.upper()}")
            print(
                f"\n[StudentAgent] Task '{title}' is due in {readable_remaining} "
                f"on {formatted_due}."
            )

            await self.send(build_message(
                TASK_JID,
                "inform",
                "add_task",
                {
                    "task_id": task_id,
                    "title": title,
                    "course": course,
                    "due_ts": due_ts,
                    "difficulty": difficulty
                }
            ))
            print(f"[StudentAgent] Action: Added task '{title}'.")
            print("[StudentAgent] Waiting for the system to store the task and evaluate urgency...\n")

        async def edit_task_flow(self):
            task_id = await self.prompt_for_existing_task_id("edit")

            print("\n================ EDIT TASK =================")
            print("What would you like to change?")
            print("1. Change task ID")
            print("2. Edit task title")
            print("3. Edit course code")
            print("4. Update deadline")
            print("5. Change difficulty")
            print("6. Mark task as completed")
            print("===========================================\n")

            choice = await self.get_valid_edit_menu_choice()

            if choice == "1":
                new_task_id = await self.prompt_for_new_unique_task_id()

                await self.send(build_message(
                    TASK_JID,
                    "inform",
                    "update_task_id",
                    {
                        "task_id": task_id,
                        "new_task_id": new_task_id
                    }
                ))
                print(f"\n[StudentAgent] Action: Changed task ID from '{task_id}' to '{new_task_id}'.")
                print("[StudentAgent] Waiting for the system to update the task...\n")

            elif choice == "2":
                new_title = await self.get_non_empty_input("Enter the new task title: ")

                await self.send(build_message(
                    TASK_JID,
                    "inform",
                    "update_title",
                    {
                        "task_id": task_id,
                        "new_title": new_title
                    }
                ))
                print(f"\n[StudentAgent] Action: Updated the title of task '{task_id}'.")
                print("[StudentAgent] Waiting for the system to apply the change...\n")

            elif choice == "3":
                new_course = await self.get_non_empty_input("Enter the new course code: ")

                await self.send(build_message(
                    TASK_JID,
                    "inform",
                    "update_course",
                    {
                        "task_id": task_id,
                        "new_course": new_course
                    }
                ))
                print(f"\n[StudentAgent] Action: Updated the course code of task '{task_id}'.")
                print("[StudentAgent] Waiting for the system to apply the change...\n")

            elif choice == "4":
                due_datetime, due_ts, remaining = await self.get_valid_datetime(
                    "Enter the new due date and time (YYYY-MM-DD HH:MM): "
                )

                readable_remaining = format_time_remaining(remaining)
                formatted_due = due_datetime.strftime("%d %B %Y at %I:%M %p")

                print(
                    f"\n[StudentAgent] Updated deadline: task '{task_id}' is now due in "
                    f"{readable_remaining} on {formatted_due}."
                )

                await self.send(build_message(
                    TASK_JID,
                    "inform",
                    "update_deadline",
                    {
                        "task_id": task_id,
                        "new_due_ts": due_ts
                    }
                ))
                print(f"[StudentAgent] Action: Updated deadline for task '{task_id}'.")
                print("[StudentAgent] Waiting for the system to recalculate priority...\n")

            elif choice == "5":
                new_difficulty = await self.get_valid_difficulty()

                await self.send(build_message(
                    TASK_JID,
                    "inform",
                    "update_difficulty",
                    {
                        "task_id": task_id,
                        "new_difficulty": new_difficulty
                    }
                ))
                print(f"\n[StudentAgent] Action: Updated difficulty of task '{task_id}' to {new_difficulty.upper()}.")
                print("[StudentAgent] Waiting for the system to apply the change...\n")

            elif choice == "6":
                await self.send(build_message(
                    TASK_JID,
                    "inform",
                    "mark_done",
                    {"task_id": task_id}
                ))
                print(f"\n[StudentAgent] Action: Marked task '{task_id}' as completed.")
                print("[StudentAgent] Waiting for the system to stop reminders...\n")

        async def run(self):
            print("\n===================================================")
            print("ASSIGNMENT DEADLINE REMINDER SYSTEM")
            print("Choose an action:")
            print("1. Add a task")
            print("2. Edit a task")
            print("3. View tasks")
            print("4. Exit simulation")
            print("===================================================\n")

            choice = await self.get_valid_main_menu_choice()

            if choice == "1":
                await self.add_task_flow()

            elif choice == "2":
                await self.edit_task_flow()

            elif choice == "3":
                await self.show_available_tasks()

            elif choice == "4":
                print("\n[System] Stopping all agents...")

                for agent in self.agent.all_agents:
                    await agent.stop()

                await asyncio.sleep(1)

                print("\n===================================================")
                print("SIMULATION COMPLETE")
                print("The Intelligent Multi-Agent Assignment Deadline Reminder System has finished running.")
                print("===================================================\n")

            await asyncio.sleep(1)

    async def setup(self):
        print("[StudentAgent] Started successfully.")
        template = Template()
        template.metadata = {"performative": "inform"}
        self.add_behaviour(self.ReceiveBehaviour(), template)
        self.add_behaviour(self.InteractiveMenuBehaviour())