"""JSON REST API for feedback entries."""

from flask import current_app, jsonify, request, url_for

from ..extensions import db
from ..models import Feedback
from ..validation import validate_feedback
from . import bp


@bp.route("/feedback", methods=["GET"])
def list_feedback():
    """Return a paginated list of feedback entries.

    Query params:
        page (int): 1-based page number (default 1).
        per_page (int): items per page (default from config, capped at 100).
    """
    page = request.args.get("page", 1, type=int)
    default_per_page = current_app.config["ITEMS_PER_PAGE"]
    per_page = request.args.get("per_page", default_per_page, type=int)
    per_page = max(1, min(per_page, 100))

    pagination = db.paginate(
        db.select(Feedback).order_by(Feedback.created_at.desc()),
        page=page,
        per_page=per_page,
        error_out=False,
    )

    return jsonify(
        {
            "items": [entry.to_dict() for entry in pagination.items],
            "pagination": {
                "page": pagination.page,
                "per_page": pagination.per_page,
                "total": pagination.total,
                "pages": pagination.pages,
                "has_next": pagination.has_next,
                "has_prev": pagination.has_prev,
            },
        }
    )


@bp.route("/feedback", methods=["POST"])
def create_feedback():
    """Create a feedback entry from a JSON payload."""
    data = request.get_json(silent=True) or {}
    name = data.get("name")
    message = data.get("message")

    errors = validate_feedback(name, message)
    if errors:
        return jsonify({"errors": errors}), 400

    entry = Feedback(name=name.strip(), message=message.strip())
    db.session.add(entry)
    db.session.commit()

    response = jsonify(entry.to_dict())
    response.status_code = 201
    response.headers["Location"] = url_for(
        "api.list_feedback", _external=False
    )
    return response
