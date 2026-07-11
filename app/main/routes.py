"""Routes for the human-facing feedback board."""

from flask import (
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from ..extensions import db
from ..models import Feedback
from ..validation import validate_feedback
from . import bp


@bp.route("/", methods=["GET"])
def index():
    """Render the paginated feedback board."""
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config["ITEMS_PER_PAGE"]

    pagination = db.paginate(
        db.select(Feedback).order_by(Feedback.created_at.desc()),
        page=page,
        per_page=per_page,
        error_out=False,
    )

    return render_template(
        "index.html",
        pagination=pagination,
        entries=pagination.items,
        max_name=current_app.config["MAX_NAME_LENGTH"],
        max_message=current_app.config["MAX_MESSAGE_LENGTH"],
    )


@bp.route("/", methods=["POST"])
def create():
    """Handle a feedback submission from the web form."""
    name = request.form.get("name", "")
    message = request.form.get("message", "")

    errors = validate_feedback(name, message)
    if errors:
        for error in errors.values():
            flash(error, "error")
        return (
            render_template(
                "index.html",
                pagination=_first_page(),
                entries=_first_page().items,
                form_name=name,
                form_message=message,
                max_name=current_app.config["MAX_NAME_LENGTH"],
                max_message=current_app.config["MAX_MESSAGE_LENGTH"],
            ),
            400,
        )

    entry = Feedback(name=name.strip(), message=message.strip())
    db.session.add(entry)
    db.session.commit()

    flash("Thanks for your feedback!", "success")
    return redirect(url_for("main.index"))


def _first_page():
    """Return the first page of feedback for re-rendering after an error."""
    return db.paginate(
        db.select(Feedback).order_by(Feedback.created_at.desc()),
        page=1,
        per_page=current_app.config["ITEMS_PER_PAGE"],
        error_out=False,
    )
