from flask import Request


def get_pagination_params(
    request: Request,
    default_limit: int = 20,
    max_limit: int = 100,
) -> tuple[int, int]:
    """
    Extract pagination parameters (limit, offset) from an HTTP request.

    Query parameters:
      - limit: max items per page
      - offset: number of items to skip
    """
    try:
        limit = int(request.args.get("limit", default_limit))
    except (TypeError, ValueError):
        limit = default_limit

    try:
        offset = int(request.args.get("offset", 0))
    except (TypeError, ValueError):
        offset = 0

    if limit <= 0:
        limit = default_limit
    if limit > max_limit:
        limit = max_limit
    if offset < 0:
        offset = 0

    return limit, offset
