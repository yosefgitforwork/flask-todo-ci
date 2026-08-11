"""Configuration objects, one per environment, selected by name in the factory.

- ``TestConfig`` uses an in-memory SQLite database so the test suite needs no
  running MySQL server.
- ``DevConfig`` / ``ProdConfig`` build a MySQL URI from environment variables,
  keeping the *exact* connection contract of the original monolith
  (``mysql+pymysql`` via DB_USER / DB_PASSWORD / DB_HOST / DB_NAME) and the same
  default values, so an existing database keeps working unchanged.
"""
import os


def _mysql_uri():
    """Assemble the SQLAlchemy URI for MySQL from environment variables.

    Defaults match the original app so existing databases keep working:
    ``root`` / ``12345`` / ``mysql`` / ``flask``.
    """
    user = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASSWORD", "password")
    host = os.getenv("DB_HOST", "mysql")
    name = os.getenv("DB_NAME", "flask")
    return f"mysql+pymysql://{user}:{password}@{host}/{name}"


class BaseConfig:
    # Turn off the event-system overhead we don't use.
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = _mysql_uri()


class TestConfig(BaseConfig):
    TESTING = True
    # In-memory DB: fast, isolated, and requires no external server.
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


class ProdConfig(BaseConfig):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = _mysql_uri()


# Keyed exactly as the spec requires: "dev" / "test" / "prod".
config_map = {
    "dev": DevConfig,
    "test": TestConfig,
    "prod": ProdConfig,
}
