from modules.database import SessionLocal
from modules.models import Task

def create_task(title, description, user_id):
    db = SessionLocal()
    new_task = Task(title=title, description=description, user_id=user_id)
    db.add(new_task)
    db.commit()
    db.close()
    return True

def get_tasks(user_id):
    db = SessionLocal()
    # Fetch all tasks belonging to this specific user
    tasks = db.query(Task).filter(Task.user_id == user_id).all()
    db.close()
    return tasks

def complete_task(task_id):
    db = SessionLocal()
    # Find the task and update its status
    task = db.query(Task).filter(Task.id == task_id).first()
    if task:
        task.status = "completed"
        db.commit()
    db.close()
    return True