from flask import Blueprint, request, jsonify
from ..repositories.report_repo import ReportRepository
from ..repositories.project_repo import ProjectRepository
from ..services.report_service import ReportService

reports_bp = Blueprint("reports", __name__)

_report_repo = ReportRepository()
_project_repo = ProjectRepository()
_report_service = ReportService(report_repo=_report_repo, project_repo=_project_repo)


@reports_bp.route("/project/<int:project_id>/daily-summary", methods=["POST"])
def request_daily_summary(project_id: int):
    """Request an asynchronous daily summary report for a project."""
    params = request.get_json() or {}

    report = _report_service.request_project_summary_report(
        project_id=project_id,
        params=params,
    )

    return jsonify(report), 202


@reports_bp.route("/<int:report_id>", methods=["GET"])
def get_report(report_id: int):
    """Fetch report by id."""
    report = _report_service.get_report(report_id=report_id)
    return jsonify(report)
