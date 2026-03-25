# Assignment Deadline Reminder System
The Assignment Deadline Reminder System is an intelligent SPADE-based multi-agent system designed to help students effectively manage assignments and avoid missing deadlines. The system distributes responsibilities across specialized agents to ensure continuous monitoring, priority evaluation, and timely reminders.

## System Architecture
The system consists of four cooperating agents:
- **StudentAgent**  
  Handles user interaction, input, and displays notifications.
- **TaskAgent**  
  Stores and manages all task-related data.
- **PriorityAgent**  
  Evaluates task urgency based on deadlines and difficulty.
- **ReminderAgent**  
  Sends reminders and escalates alerts as deadlines approach.


## Key Features
- Add and manage assignments  
- Edit task details (title, course, deadline, difficulty)  
- View all tasks in the system  
- Mark tasks as completed  
- Continuous deadline monitoring  
- Automatic priority evaluation  
- Escalating reminders (low → medium → high → urgent → overdue)  
- Notification system with urgent alerts  


## Requirements
- Python 3.10 or higher  
- SPADE (Smart Python Agent Development Environment)  


## Setup Guide
### 1. Clone or download the project
```bash
git clone https://github.com/ewurafuaa/403SemesterProject.git
```

### 2. Create a virtual environment
```bash
python -m venv .venv
```

### 3. Activate the environment
```bash
source .venv/bin/activate
```

### 4. Upgrade pip
```bash
python -m pip install --upgrade pip
```

### 5. Install dependencies
```bash
pip install spade
```

### 6. Run spade
```bash
spade run
```

### 7. In a new terminal, activate the environment
```bash
source .venv/bin/activate
```

### 8. Run the system
Start the system with:
```bash
python main.py
```

---

When the system starts, the following menu is displayed:
1. Add a task
2. Edit a task
3. View tasks
4. Notifications
5. Exit simulation

## System Behavior
- Tasks are continuously monitored by the system
- Priority is automatically updated based on time remaining
- Reminders are sent and escalated as deadlines approach
- Urgent tasks are highlighted in the main menu
- Completed tasks stop generating reminders

## Objectives Achieved
- Efficient task tracking
- Automated priority evaluation
- Real-time reminder generation
- Reduced risk of missed deadlines
- Loosely coupled multi-agent architecture