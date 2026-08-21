import logging

import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlmodel import Session, SQLModel, create_engine

from core.settings.default import AppSettings
from core.database.load_database_data import seed_from_yaml

logger = logging.getLogger(__name__)

settings = AppSettings()
engine = create_engine(settings.db_url, echo=False)


def create_tables() -> None:
    SQLModel.metadata.create_all(engine)
    logger.info("All tables created / verified.")


def _database_exists(cursor, db_name: str) -> bool:
    cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
    return cursor.fetchone() is not None


def _create_database(cursor, db_name: str) -> None:
    cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))


def create_database_if_not_exists() -> None:
    conn = psycopg2.connect(
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        database="postgres",
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()

    if not _database_exists(cursor, settings.DB_NAME):
        _create_database(cursor, settings.DB_NAME)
        logger.info("Database '%s' created.", settings.DB_NAME)
    else:
        logger.info("Database '%s' already exists.", settings.DB_NAME)

    cursor.close()
    conn.close()


def seed_lookup_tables() -> None:
    with Session(engine) as session:
        inserted = seed_from_yaml(session, settings.DATA_YALM)

    total = sum(len(v) for v in inserted.values())
    if total:
        # Counts, not contents: dumping 437 catalog names into production logs
        # buries every other line and costs money on hosted log storage.
        logger.info(
            "Seeded %d new rows (languages: %d, techs: %d, addons: %d).",
            total,
            len(inserted["programming_languages"]),
            len(inserted["techs"]),
            len(inserted["addons"]),
        )
        logger.debug("Seeded values: %s", inserted)
    else:
        logger.info("Seed: all lookup values already present, nothing inserted.")


def init_db() -> None:
    """Prepare the database for serving.

    On a managed platform the database is provisioned for us and the
    application user usually cannot connect to the maintenance database at all,
    so CREATE DATABASE is skipped whenever DATABASE_URL is supplied
    (spec 004, Edge Cases). Table creation stays idempotent either way: in the
    container the schema already came from `alembic upgrade head`.
    """
    if settings.DATABASE_URL:
        logger.info("DATABASE_URL provided; skipping database creation.")
    else:
        create_database_if_not_exists()

    create_tables()
    seed_lookup_tables()


def get_db():
    with Session(engine) as session:
        yield session
