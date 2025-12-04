from typing import Optional
from ..models import Report, Project


class ReportRepository:
    """Persistence operations for Report entity."""

    def create(self, project: Project, report_type: str, params: dict | None) -> Report:
        report = Report(project=project, type=report_type, params=params or {}, status="pending")
        return report

    def get(self, report_id: int) -> Optional[Report]:
        return Report.get(id=report_id)
