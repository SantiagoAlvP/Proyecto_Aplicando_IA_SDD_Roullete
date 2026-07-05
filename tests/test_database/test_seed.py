import pytest
import yaml
from unittest.mock import MagicMock, patch
from core.database.load_database_data import seed_from_yaml


class TestSeedFromYaml:
    def test_inserts_all_when_db_is_empty(self, session, yaml_file):
        with (
            patch(
                "core.database.crud.ProgrammingLanguageCRUD.get_by_name",
                return_value=None,
            ),
            patch("core.database.crud.TechCRUD.get_by_name", return_value=None),
            patch("core.database.crud.AddonCRUD.get_by_name", return_value=None),
            patch("core.database.crud.ProgrammingLanguageCRUD.create") as mock_lang,
            patch("core.database.crud.TechCRUD.create") as mock_tech,
            patch("core.database.crud.AddonCRUD.create") as mock_addon,
        ):
            result = seed_from_yaml(session, yaml_file)

        assert result["programming_languages"] == ["Python", "Rust", "C++"]
        assert result["techs"] == ["Git", "Docker", "Kubernetes"]
        assert result["addons"] == ["VSCode", "Sublime Text", "Postman"]

        assert mock_lang.call_count == 3
        assert mock_tech.call_count == 3
        assert mock_addon.call_count == 3

    def test_create_called_with_correct_names(self, session, yaml_file):
        with (
            patch(
                "core.database.crud.ProgrammingLanguageCRUD.get_by_name",
                return_value=None,
            ),
            patch("core.database.crud.TechCRUD.get_by_name", return_value=None),
            patch("core.database.crud.AddonCRUD.get_by_name", return_value=None),
            patch("core.database.crud.ProgrammingLanguageCRUD.create") as mock_lang,
            patch("core.database.crud.TechCRUD.create") as mock_tech,
            patch("core.database.crud.AddonCRUD.create") as mock_addon,
        ):
            seed_from_yaml(session, yaml_file)

        mock_lang.assert_any_call(session, "Python")
        mock_lang.assert_any_call(session, "Rust")
        mock_lang.assert_any_call(session, "C++")
        mock_tech.assert_any_call(session, "Docker")
        mock_addon.assert_any_call(session, "VSCode")

    def test_skips_all_when_everything_exists(self, session, yaml_file):
        existing = MagicMock()

        with (
            patch(
                "core.database.crud.ProgrammingLanguageCRUD.get_by_name",
                return_value=existing,
            ),
            patch("core.database.crud.TechCRUD.get_by_name", return_value=existing),
            patch("core.database.crud.AddonCRUD.get_by_name", return_value=existing),
            patch("core.database.crud.ProgrammingLanguageCRUD.create") as mock_lang,
            patch("core.database.crud.TechCRUD.create") as mock_tech,
            patch("core.database.crud.AddonCRUD.create") as mock_addon,
        ):
            result = seed_from_yaml(session, yaml_file)

        assert result == {
            "programming_languages": [],
            "techs": [],
            "addons": [],
        }
        mock_lang.assert_not_called()
        mock_tech.assert_not_called()
        mock_addon.assert_not_called()

    def test_partial_insert_when_some_exist(self, session, yaml_file):
        existing = MagicMock()

        def lang_exists(sess, name):
            return existing if name == "Python" else None

        with (
            patch(
                "core.database.crud.ProgrammingLanguageCRUD.get_by_name",
                side_effect=lang_exists,
            ),
            patch("core.database.crud.TechCRUD.get_by_name", return_value=existing),
            patch("core.database.crud.AddonCRUD.get_by_name", return_value=None),
            patch("core.database.crud.ProgrammingLanguageCRUD.create") as mock_lang,
        ):
            result = seed_from_yaml(session, yaml_file)

        # Python was skipped, Rust and C++ were inserted
        assert "Python" not in result["programming_languages"]
        assert "Rust" in result["programming_languages"]
        assert "C++" in result["programming_languages"]
        assert mock_lang.call_count == 2
        assert result["techs"] == []
        assert len(result["addons"]) == 3

    def test_empty_yaml_inserts_nothing(self, session, empty_yaml_file):
        with (
            patch("core.database.crud.ProgrammingLanguageCRUD.create") as mock_lang,
            patch("core.database.crud.TechCRUD.create") as mock_tech,
            patch("core.database.crud.AddonCRUD.create") as mock_addon,
        ):
            result = seed_from_yaml(session, empty_yaml_file)

        assert result == {
            "programming_languages": [],
            "techs": [],
            "addons": [],
        }
        mock_lang.assert_not_called()
        mock_tech.assert_not_called()
        mock_addon.assert_not_called()

    def test_strips_whitespace_from_names(self, session, tmp_path):
        yaml_file = tmp_path / "padded.yaml"
        yaml_file.write_text(
            """
programming_languages:
  - "           Python  "
technologies: []
addons: []
"""
        )

        with (
            patch(
                "core.database.crud.ProgrammingLanguageCRUD.get_by_name",
                return_value=None,
            ),
            patch("core.database.crud.ProgrammingLanguageCRUD.create") as mock_create,
        ):
            seed_from_yaml(session, str(yaml_file))

        mock_create.assert_called_once_with(session, "Python")

    def test_raises_on_missing_file(self, session):
        with pytest.raises(FileNotFoundError):
            seed_from_yaml(session, "/nonexistent/path/skills.yaml")

    def test_raises_on_invalid_yaml_syntax(self, session, tmp_path):
        yaml_file = tmp_path / "corrupted.yaml"
        yaml_file.write_text(
            """
    programming_languages:
      - Python
      - : bad_key
        :::invalid:::
            unexpected: [
    addons: [unclosed
    """
        )
        with pytest.raises(yaml.YAMLError):
            seed_from_yaml(session, str(yaml_file))

    def test_raises_on_wrong_type_for_list(self, session, tmp_path):
        yaml_file = tmp_path / "wrong_type.yaml"
        yaml_file.write_text(
            """
    programming_languages: "Python"
    techs: 42
    addons: true
    """
        )
        with pytest.raises(TypeError):
            seed_from_yaml(session, str(yaml_file))

    def test_handles_none_values_in_list(self, session, tmp_path):
        """A list entry is null/None — str(None).strip() produces 'None', which is wrong."""
        yaml_file = tmp_path / "null_entry.yaml"
        yaml_file.write_text(
            """
    programming_languages:
      - Python
      -
      - Rust
    techs: []
    addons: []
    """
        )
        with (
            patch(
                "core.database.crud.ProgrammingLanguageCRUD.get_by_name",
                return_value=None,
            ),
            patch("core.database.crud.ProgrammingLanguageCRUD.create") as mock_create,
        ):
            seed_from_yaml(session, str(yaml_file))

        called_names = [call.args[1] for call in mock_create.call_args_list]
        assert "None" not in called_names
        assert "Python" in called_names
        assert "Rust" in called_names
