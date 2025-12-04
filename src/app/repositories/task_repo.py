from typing import Iterable, Optional
from pony.orm import select
from ..models import Task, TaskEvent, Project, User


class TaskRepository:
    """Persistence operations for Task entity."""

    def create(
        self,
        project: Project,
        title: str,
        description: str | None,
        assignee: User | None,
    ) -> Task:
        task = Task(
            project=project,
            title=title,
            description=description,
            assignee=assignee,
            status="todo",
        )
        TaskEvent(task=task, type="created", payload={})
        return task

    def get(self, task_id: int) -> Optional[Task]:
        return Task.get(id=task_id)

    def list_by_project(self, project: Project, limit: int, offset: int) -> Iterable[Task]:
        query = select(t for t in Task if t.project == project).order_by(lambda t: t.id)
        return query.limit(limit, offset=offset)[:]

    def add_event(self, task: Task, event_type: str, payload: dict) -> TaskEvent:
        event = TaskEvent(task=task, type=event_type, payload=payload)
        return event
