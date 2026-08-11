"""Shared extension instances.

Each extension is created here *without* an app attached. The application
factory (`create_app`) later calls ``init_app(app)`` on each one. This is the
canonical Flask pattern: models and blueprints can ``from .extensions import db``
without importing the app object itself, which would create an import cycle.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

db = SQLAlchemy()
migrate = Migrate()
cors = CORS()
