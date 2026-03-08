import json
import os
import threading
import time
import uuid
from datetime import datetime, timedelta

DATA_DIR = os.path.join("Backend", "Data")
TASKS_FILE = os.path.join(DATA_DIR, "tasks.json")

# Ensure Data directory exists
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Initialize file if not exists
if not os.path.exists(TASKS_FILE):
    with open(TASKS_FILE, "w", encoding='utf-8') as f:
        json.dump([], f)

file_lock = threading.Lock()

def log_info(msg):
    print(f"[TASKS-INFO] {msg}")

def create_task(title, priority="Medium", due_date=None):
    """Create a new task with optional due date and priority."""
    task_id = f"task_{uuid.uuid4().hex[:8]}"
    
    task = {
        "id": task_id,
        "title": title,
        "priority": priority,
        "due_date": due_date,
        "completed": False,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    with file_lock:
        try:
            with open(TASKS_FILE, "r", encoding='utf-8') as f:
                tasks = json.load(f)
            
            tasks.append(task)
            
            with open(TASKS_FILE, "w", encoding='utf-8') as f:
                json.dump(tasks, f, indent=4)
            
            log_info(f"Created task: {title} (ID: {task_id})")
            return task_id
        except Exception as e:
            print(f"[TASKS-ERROR] Failed to create task: {e}")
            return None

def edit_task(task_id, title=None, priority=None, due_date=None):
    """Edit an existing task's properties."""
    with file_lock:
        try:
            with open(TASKS_FILE, "r", encoding='utf-8') as f:
                tasks = json.load(f)
            
            updated = False
            for task in tasks:
                if task["id"] == task_id:
                    if title:
                        task["title"] = title
                    if priority:
                        task["priority"] = priority
                    if due_date:
                        task["due_date"] = due_date
                    task["updated_at"] = datetime.now().isoformat()
                    updated = True
                    break
            
            if updated:
                with open(TASKS_FILE, "w", encoding='utf-8') as f:
                    json.dump(tasks, f, indent=4)
                log_info(f"Updated task: {task_id}")
                return True
            else:
                return False
        except Exception as e:
            print(f"[TASKS-ERROR] Failed to edit task: {e}")
            return False

def delete_task(task_id):
    """Delete a specific task."""
    with file_lock:
        try:
            with open(TASKS_FILE, "r", encoding='utf-8') as f:
                tasks = json.load(f)
            
            tasks = [task for task in tasks if task["id"] != task_id]
            
            with open(TASKS_FILE, "w", encoding='utf-8') as f:
                json.dump(tasks, f, indent=4)
            
            log_info(f"Deleted task: {task_id}")
            return True
        except Exception as e:
            print(f"[TASKS-ERROR] Failed to delete task: {e}")
            return False

def complete_task(task_id, completed=True):
    """Mark a task as completed or incomplete."""
    with file_lock:
        try:
            with open(TASKS_FILE, "r", encoding='utf-8') as f:
                tasks = json.load(f)
            
            updated = False
            for task in tasks:
                if task["id"] == task_id:
                    task["completed"] = completed
                    task["updated_at"] = datetime.now().isoformat()
                    updated = True
                    break
            
            if updated:
                with open(TASKS_FILE, "w", encoding='utf-8') as f:
                    json.dump(tasks, f, indent=4)
                log_info(f"Task {task_id} marked as {'completed' if completed else 'incomplete'}")
                return True
            else:
                return False
        except Exception as e:
            print(f"[TASKS-ERROR] Failed to complete task: {e}")
            return False

def get_tasks(completed=None, priority=None, due_date=None):
    """Get all tasks with optional filters."""
    try:
        with open(TASKS_FILE, "r", encoding='utf-8') as f:
            tasks = json.load(f)
        
        filtered = tasks
        
        if completed is not None:
            filtered = [task for task in filtered if task["completed"] == completed]
        
        if priority:
            filtered = [task for task in filtered if task["priority"].lower() == priority.lower()]
        
        if due_date:
            try:
                target_date = datetime.fromisoformat(due_date).date()
                filtered = [task for task in filtered if task["due_date"] and 
                          datetime.fromisoformat(task["due_date"]).date() == target_date]
            except ValueError:
                pass
        
        return filtered
    except Exception as e:
        print(f"[TASKS-ERROR] Failed to get tasks: {e}")
        return []

def get_task_statistics():
    """Get task statistics (total, completed, pending, by priority)."""
    tasks = get_tasks()
    
    statistics = {
        "total": len(tasks),
        "completed": len([task for task in tasks if task["completed"]]),
        "pending": len([task for task in tasks if not task["completed"]]),
        "by_priority": {
            "High": len([task for task in tasks if task["priority"] == "High"]),
            "Medium": len([task for task in tasks if task["priority"] == "Medium"]),
            "Low": len([task for task in tasks if task["priority"] == "Low"])
        }
    }
    
    return statistics

def search_tasks(keyword):
    """Search tasks by keyword in title."""
    tasks = get_tasks()
    return [task for task in tasks if keyword.lower() in task["title"].lower()]

def get_overdue_tasks():
    """Get tasks that are overdue but not completed."""
    now = datetime.now().date()
    tasks = get_tasks(completed=False)
    
    overdue = []
    for task in tasks:
        if task["due_date"]:
            try:
                due_date = datetime.fromisoformat(task["due_date"]).date()
                if due_date < now:
                    overdue.append(task)
            except ValueError:
                continue
    
    return overdue

def get_upcoming_tasks(days=7):
    """Get tasks due in the next specified number of days."""
    now = datetime.now().date()
    future = now + timedelta(days=days)
    tasks = get_tasks(completed=False)
    
    upcoming = []
    for task in tasks:
        if task["due_date"]:
            try:
                due_date = datetime.fromisoformat(task["due_date"]).date()
                if now <= due_date <= future:
                    upcoming.append(task)
            except ValueError:
                continue
    
    return upcoming

def format_task(task):
    """Format a single task for display."""
    status = "[X]" if task["completed"] else "[ ]"
    priority = task["priority"][0].upper()
    due_date = f" (Due: {task['due_date']})" if task["due_date"] else ""
    return f"{status} [{priority}] {task['title']}{due_date}"

def format_tasks_list(tasks):
    """Format a list of tasks for display."""
    if not tasks:
        return "No tasks found."
    
    formatted = []
    for task in tasks:
        formatted.append(format_task(task))
    
    return "\n".join(formatted)

def format_statistics(stats):
    """Format task statistics for display."""
    return (
        f"Tasks Statistics:\n"
        f"- Total: {stats['total']}\n"
        f"- Completed: {stats['completed']}\n"
        f"- Pending: {stats['pending']}\n"
        f"- High Priority: {stats['by_priority']['High']}\n"
        f"- Medium Priority: {stats['by_priority']['Medium']}\n"
        f"- Low Priority: {stats['by_priority']['Low']}"
    )

if __name__ == "__main__":
    # Test task management functions
    print("Testing Tasks Management...")
    
    print("\n1. Creating a task:")
    task_id = create_task("Buy groceries", "High", "2024-12-31")
    print(f"Created task with ID: {task_id}")
    
    print("\n2. Creating another task:")
    task2_id = create_task("Finish report", "Medium", "2025-01-15")
    print(f"Created task with ID: {task2_id}")
    
    print("\n3. Getting all tasks:")
    all_tasks = get_tasks()
    print(format_tasks_list(all_tasks))
    
    print("\n4. Completing a task:")
    complete_task(task_id)
    print("Task marked as completed")
    
    print("\n5. Getting completed tasks:")
    completed_tasks = get_tasks(completed=True)
    print(format_tasks_list(completed_tasks))
    
    print("\n6. Task statistics:")
    stats = get_task_statistics()
    print(format_statistics(stats))
    
    print("\n7. Searching for tasks containing 'report':")
    search_results = search_tasks("report")
    print(format_tasks_list(search_results))
    
    print("\n8. Deleting tasks:")
    delete_task(task_id)
    delete_task(task2_id)
    print("All test tasks deleted")
