"""WSGI entrypoint used by gunicorn in production: ``gunicorn wsgi:app``.

Also the target of ``FLASK_APP=wsgi.py`` so the ``flask db ...`` CLI can find the
app. Defaults to the ``prod`` config; override with the FLASK_CONFIG env var.
"""
import os

from app import create_app

app = create_app(os.getenv("FLASK_CONFIG", "prod"))
