"""Todos REST API blueprint.

Pure JSON in, pure JSON out — no templates. Each route maps one HTTP verb to a
CRUD operation and returns the status code that good REST hygiene (and the spec)
expects: 200 read, 201 created, 204 no-content, 400 bad request, 404 not found.
"""
from flask import Blueprint, abort, jsonify, request

from ..extensions import db
from ..models import Todo

# The url_prefix lives on the blueprint, so routes below are relative to it.
bp = Blueprint("todos", __name__, url_prefix="/api/todos")

# List of allowed priority values
VALID_PRIORITIES = {"low", "medium", "high"}


@bp.get("")
def list_todos():
    """GET /api/todos -> 200, all todos ordered by id."""
    # SQLAlchemy 2.x style: select() + session.scalars() rather than Query.all().
    todos = db.session.scalars(db.select(Todo).order_by(Todo.id)).all()
    return jsonify([t.to_dict() for t in todos]), 200


@bp.post("")
def create_todo():
    """POST /api/todos -> 201 created, or 400 if title is missing/empty or invalid priority."""
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    if not title:
        abort(400, description="title is required and must be non-empty")

    # Handle priority with default fallback to 'medium'
    priority = data.get("priority", "medium")
    if priority not in VALID_PRIORITIES:
        abort(
            400,
            description=f"invalid priority '{priority}'. Must be one of: {sorted(list(VALID_PRIORITIES))}",
        )

    todo = Todo(
        title=title,
        complete=bool(data.get("complete", False)),
        priority=priority,
    )
    db.session.add(todo)
    db.session.commit()
    return jsonify(todo.to_dict()), 201


@bp.patch("/<int:todo_id>")
def update_todo(todo_id):
    """PATCH /api/todos/<id> -> 200 partial update, or 404 if not found."""
    # SQLAlchemy 2.x PK lookup — replaces the deprecated Query.get().
    todo = db.session.get(Todo, todo_id)
    if todo is None:
        abort(404, description=f"todo {todo_id} not found")

    data = request.get_json(silent=True) or {}

    # Partial update: only touch fields the client actually sent.
    if "title" in data:
        title = (data.get("title") or "").strip()
        if not title:
            abort(400, description="title must be non-empty")
        todo.title = title

    if "complete" in data:
        todo.complete = bool(data["complete"])

    # Priority update (only if key is explicitly present in JSON)
    if "priority" in data:
        priority = data["priority"]
        if priority not in VALID_PRIORITIES:
            abort(
                400,
                description=f"invalid priority '{priority}'. Must be one of: {sorted(list(VALID_PRIORITIES))}",
            )
        todo.priority = priority

    db.session.commit()
    return jsonify(todo.to_dict()), 200


@bp.delete("/<int:todo_id>")
def delete_todo(todo_id):
    """DELETE /api/todos/<id> -> 204 no content, or 404 if not found."""
    todo = db.session.get(Todo, todo_id)
    if todo is None:
        abort(404, description=f"todo {todo_id} not found")

    db.session.delete(todo)
    db.session.commit()
    # 204 responses carry no body.
    return "", 204