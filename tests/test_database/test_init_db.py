"""Spec 004, HU-02: booting against a managed database must not try to create it."""

from unittest.mock import patch

from core.database import database


def test_managed_database_url_skips_create_database() -> None:
    """Railway's app user cannot connect to the maintenance database at all."""
    with (
        patch.object(database.settings, "DATABASE_URL", "postgresql://u:p@host/db"),
        patch.object(database, "create_database_if_not_exists") as create_db,
        patch.object(database, "create_tables"),
        patch.object(database, "seed_lookup_tables"),
    ):
        database.init_db()

    create_db.assert_not_called()


def test_local_setup_still_creates_the_database() -> None:
    with (
        patch.object(database.settings, "DATABASE_URL", None),
        patch.object(database, "create_database_if_not_exists") as create_db,
        patch.object(database, "create_tables"),
        patch.object(database, "seed_lookup_tables"),
    ):
        database.init_db()

    create_db.assert_called_once()


def test_tables_and_seed_always_run() -> None:
    with (
        patch.object(database.settings, "DATABASE_URL", "postgresql://u:p@host/db"),
        patch.object(database, "create_database_if_not_exists"),
        patch.object(database, "create_tables") as create_tables,
        patch.object(database, "seed_lookup_tables") as seed,
    ):
        database.init_db()

    create_tables.assert_called_once()
    seed.assert_called_once()
