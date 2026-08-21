import psycopg
from sqlmodel import Session, text
from core.database.database import engine
from core.settings.default import AppSettings

import pytest

# Opt-in: these hit real services. See pyproject [tool.pytest.ini_options].
pytestmark = pytest.mark.integration


def test_postgres_is_alive_psycopg():
    settings = AppSettings()
    conn = psycopg.connect(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        dbname=settings.DB_NAME,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
    )

    with conn.cursor() as cur:
        cur.execute("SELECT 1")
        row = cur.fetchone()

        assert row is not None
        assert row[0] == 1
    conn.close()


def test_postgres_is_alive_sqlmodel():
    with Session(engine) as session:
        # Raw SQL smoke check: session.execute is the right API here, exec() is
        # for SQLModel selects.
        result = session.execute(text("SELECT 1"))  # ty: ignore[deprecated]
        row = result.one()

        assert row[0] == 1
