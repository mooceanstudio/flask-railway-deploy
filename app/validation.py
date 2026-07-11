"""Input validation shared by the web form and the JSON API."""

from __future__ import annotations

from flask import current_app


def validate_feedback(name: str | None, message: str | None) -> dict[str, str]:
    """Validate a feedback submission.

    Returns a mapping of ``field -> error message``. An empty mapping means
    the submission is valid. Centralising the rules keeps the HTML form and
    the REST API in perfect agreement.
    """
    errors: dict[str, str] = {}

    max_name = current_app.config["MAX_NAME_LENGTH"]
    max_message = current_app.config["MAX_MESSAGE_LENGTH"]

    clean_name = (name or "").strip()
    clean_message = (message or "").strip()

    if not clean_name:
        errors["name"] = "Name is required."
    elif len(clean_name) > max_name:
        errors["name"] = f"Name must be at most {max_name} characters."

    if not clean_message:
        errors["message"] = "Message is required."
    elif len(clean_message) > max_message:
        errors["message"] = (
            f"Message must be at most {max_message} characters."
        )

    return errors
