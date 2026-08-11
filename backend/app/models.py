"""Data models.

The ``Todo`` table has been updated to include a ``priority`` field alongside 
the original columns ``id``, ``title``, and ``complete``.
"""
from .extensions import db


class Todo(db.Model):
    # Explicit table name that matches SQLAlchemy's default for the class `Todo`
    __tablename__ = "todo"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    complete = db.Column(db.Boolean, default=False, nullable=False)
    
    # NEW FIELD: Enum restricted to 'low', 'medium', 'high'
    priority = db.Column(
        db.Enum("low", "medium", "high", name="priority_enum"),
        default="medium",
        nullable=False,
    )

    def to_dict(self):
        """Serialize to the JSON shape the API and the frontend agree on."""
        return {
            "id": self.id,
            "title": self.title,
            "complete": self.complete,
            "priority": self.priority,  # Included in JSON response
        }

    def __repr__(self):
        return f"<Todo {self.id} {self.title!r} complete={self.complete} priority={self.priority!r}>"