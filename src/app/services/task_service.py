from typing import List
from pony.orm import db_session
from ..repositories.task_repo import TaskRepository
from ..repositories.project_repo import ProjectRepository
from ..repositories.user_repo import UserRepository
from ..exceptions import ValidationError, NotFoundError


class TaskService:
    """Business logic for tasks and task events."""

    VALID_STATUSES = {"todo", "in_progress", "done"}

    def __init__(
        self,
        task_repo: TaskRepository,
        project_repo: ProjectRepository,
        user_repo: UserRepository,
    ) -> None:
        self.task_repo = task_repo
        self.project_repo = project_repo
        self.user_repo = user_repo

    @db_session
    def create_task(
        self,
        project_id: int,
        title: str,
        description: str | None,
        assignee_id: int | None,
    ) -> dict:
        project = self.project_repo.get(project_id)
        if project is None:
            raise NotFoundError("Project not found")

        if not title or not title.strip():
            raise ValidationError("Task title cannot be empty")

        assignee = self.user_repo.get(assignee_id) if assignee_id else None
        task = self.task_repo.create(project=project, title=title, description=description, assignee=assignee)
        return task.to_dict()

    @db_session
    def list_tasks_for_project(self, project_id: int, limit: int, offset: int) -> List[dict]:
        project = self.project_repo.get(project_id)
        if project is None:
            raise NotFoundError("Project not found")

        tasks = self.task_repo.list_by_project(project, limit=limit, offset=offset)
        return [t.to_dict() for t in tasks]

    @db_session
    def update_status(self, task_id: int, new_status: str) -> dict:
        if new_status not in self.VALID_STATUSES:
            raise ValidationError("Invalid task status")

        task = self.task_repo.get(task_id)
        if task is None:
            raise NotFoundError("Task not found")

        old_status = task.status
        if old_status == new_status:
            return task.to_dict()

        task.status = new_status
        if new_status == "done" and task.done_at is None:
            from datetime import datetime
            task.done_at = datetime.utcnow()

        self.task_repo.add_event(
            task=task,
            event_type="status_change",
            payload={"from": old_status, "to": new_status},
        )

        return task.to_dict()
