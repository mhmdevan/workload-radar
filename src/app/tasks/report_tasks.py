from datetime import datetime, timedelta
from pony.orm import db_session, select
from ..extensions import celery
from ..models import Report, Task, db


def _calculate_avg_lead_time_days(project_id: int, since: datetime) -> float | None:
    """Calculate average lead time in days for done tasks since the given date using raw SQL."""
    sql = """
        WITH done_tasks AS (
            SELECT
                id,
                EXTRACT(EPOCH FROM (done_at - created_at)) / 86400.0 AS lead_time_days
            FROM tasks
            WHERE project = $project_id
              AND status = 'done'
              AND done_at IS NOT NULL
              AND done_at >= $since
        )
        SELECT AVG(lead_time_days)
        FROM done_tasks
    """
    result = db.select(sql, project_id=project_id, since=since)
    avg_value = next(iter(result), None)
    return float(avg_value) if avg_value is not None else None


@celery.task(name="reports.generate_project_summary")
@db_session
def generate_project_summary(report_id: int) -> None:
    """Background task to compute summary metrics for a project's report."""
    report = Report.get(id=report_id)
    if report is None:
        return

    project = report.project
    now = datetime.utcnow()
    since = now - timedelta(days=30)

    statuses = ("todo", "in_progress", "done")
    status_counts = {
        status: select(
            t for t in Task if t.project == project and t.status == status
        ).count()
        for status in statuses
    }

    avg_lead_time_days = _calculate_avg_lead_time_days(project.id, since)

    report.result = {
        "project_id": project.id,
        "generated_at": now.isoformat(),
        "status_counts": status_counts,
        "avg_lead_time_days_last_30_days": avg_lead_time_days,
    }
    report.status = "ready"
    report.finished_at = now
