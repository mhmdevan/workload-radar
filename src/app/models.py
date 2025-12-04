from datetime import datetime
from pony.orm import Database, PrimaryKey, Required, Optional, Set, Json

# Single shared database instance
db = Database()


class User(db.Entity):
    """System user."""
    _table_ = "users"

    id = PrimaryKey(int, auto=True)
    email = Required(str, unique=True)
    name = Required(str)
    password_hash = Required(str)
    created_at = Required(datetime, default=datetime.utcnow)

    projects = Set("Project")
    tasks = Set("Task", reverse="assignee")


class Project(db.Entity):
    """Project entity representing a logical work container."""
    _table_ = "projects"

    id = PrimaryKey(int, auto=True)
    name = Required(str)
    owner = Required(User)
    created_at = Required(datetime, default=datetime.utcnow)

    tasks = Set("Task")
    reports = Set("Report")


class Task(db.Entity):
    """Work task belonging to a project."""
    _table_ = "tasks"

    id = PrimaryKey(int, auto=True)
    project = Required(Project)
    title = Required(str)
    description = Optional(str)
    status = Required(str, default="todo")  # "todo" | "in_progress" | "done"
    priority = Required(int, default=2)     # 1-high, 2-normal, 3-low
    assignee = Optional(User)
    created_at = Required(datetime, default=datetime.utcnow)
    done_at = Optional(datetime)

    events = Set("TaskEvent")


class TaskEvent(db.Entity):
    """Event generated when a task changes state or receives updates."""
    _table_ = "task_events"

    id = PrimaryKey(int, auto=True)
    task = Required(Task)
    type = Required(str)        # "created" | "status_change" | "comment" | ...
    payload = Optional(Json)    # Additional event details
    created_at = Required(datetime, default=datetime.utcnow)


class Report(db.Entity):
    """Analytical report for a project."""
    _table_ = "reports"

    id = PrimaryKey(int, auto=True)
    project = Required(Project)
    type = Required(str)        # "daily_summary" | "custom_range" | ...
    params = Optional(Json)     # Filter parameters
    status = Required(str, default="pending")  # "pending" | "ready" | "failed"
    result = Optional(Json)     # Computed metrics
    created_at = Required(datetime, default=datetime.utcnow)
    finished_at = Optional(datetime)
