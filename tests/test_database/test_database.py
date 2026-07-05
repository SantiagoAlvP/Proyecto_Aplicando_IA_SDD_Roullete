from unittest.mock import MagicMock

from core.database.database import _database_exists, _create_database


class TestDatabaseExists:
    def test_returns_true_when_db_found(self, mock_cursor):
        mock_cursor.fetchone.return_value = (1,)

        result = _database_exists(mock_cursor, "mydb")

        assert result is True

    def test_returns_false_when_db_not_found(self, mock_cursor):
        mock_cursor.fetchone.return_value = None

        result = _database_exists(mock_cursor, "mydb")

        assert result is False

    def test_executes_correct_query(self, mock_cursor):
        mock_cursor.fetchone.return_value = None

        _database_exists(mock_cursor, "mydb")

        mock_cursor.execute.assert_called_once_with(
            "SELECT 1 FROM pg_database WHERE datname = %s", ("mydb",)
        )

    def test_passes_db_name_as_parameter(self, mock_cursor):
        mock_cursor.fetchone.return_value = None

        _database_exists(mock_cursor, "custom_db_name")

        args = mock_cursor.execute.call_args[0]
        assert args[1] == ("custom_db_name",)


class TestCreateDatabase:
    def test_calls_cursor_execute(self, mock_cursor):
        _create_database(mock_cursor, "mydb")

        mock_cursor.execute.assert_called_once()

    def test_execute_called_once_per_call(self, mock_cursor):
        _create_database(mock_cursor, "mydb")

        assert mock_cursor.execute.call_count == 1

    def test_different_db_names_produce_different_calls(self, mock_cursor):
        cursor_a = MagicMock()
        cursor_b = MagicMock()

        _create_database(cursor_a, "db_one")
        _create_database(cursor_b, "db_two")

        # Both executed exactly once, with different inputs
        assert cursor_a.execute.call_count == 1
        assert cursor_b.execute.call_count == 1
        assert cursor_a.execute.call_args != cursor_b.execute.call_args
