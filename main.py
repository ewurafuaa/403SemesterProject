import asyncio
import spade

from agents.student_agent import StudentAgent
from agents.task_agent import TaskAgent
from agents.priority_agent import PriorityAgent
from agents.reminder_agent import ReminderAgent
from config import STUDENT_JID, TASK_JID, PRIORITY_JID, REMINDER_JID, PASSWORD


async def main():
    student = StudentAgent(STUDENT_JID, PASSWORD)
    task = TaskAgent(TASK_JID, PASSWORD)
    priority = PriorityAgent(PRIORITY_JID, PASSWORD)
    reminder = ReminderAgent(REMINDER_JID, PASSWORD)

    student.all_agents = [student, task, priority, reminder]

    await task.start(auto_register=True)
    await priority.start(auto_register=True)
    await reminder.start(auto_register=True)
    await student.start(auto_register=True)

    while any(agent.is_alive() for agent in [student, task, priority, reminder]):
        await asyncio.sleep(1)


if __name__ == "__main__":
    spade.run(main())