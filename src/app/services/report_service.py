from typing import Any, Dict
from pony.orm import db_session
from ..repositories.report_repo import ReportRepository
from ..repositories.project_repo import ProjectRepository
from ..tasks.report_tasks import generate_project_summary
from ..exceptions import NotFoundError


class ReportService:
    """Business logic for creating and reading reports."""

    def __init__(
        self,
        report_repo: ReportRepository,
        project_repo: ProjectRepository,
    ) -> None:
        self.report_repo = report_repo
        self.project_repo = project_repo

    @db_session
    def request_project_summary_report(self, project_id: int, params: Dict[str, Any] | None) -> dict:
        project = self.project_repo.get(project_id)
        if project is None:
            raise NotFoundError("Project not found")

        report = self.report_repo.create(project=project, report_type="daily_summary", params=params or {})
        report_id = report.id
        generate_project_summary.delay(report_id)
        return report.to_dict()

    @db_session
    def get_report(self, report_id: int) -> dict:
        report = self.report_repo.get(report_id)
        if report is None:
            raise NotFoundError("Report not found")
        return report.to_dict()
