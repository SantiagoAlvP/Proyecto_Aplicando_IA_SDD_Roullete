from unittest.mock import AsyncMock, MagicMock

import pytest

from core.ensemble_project.ensemble_project_service import ProjectGeneratorService


@pytest.mark.asyncio
async def test_regenerate_description_preserves_project_combination() -> None:
    project = {
        "id": 7,
        "programming_language": "Python",
        "technologies": "FastAPI",
        "addons": "PostgreSQL",
        "level": 3,
        "extras": [
            {
                "programming_language": "TypeScript",
                "technologies": None,
                "addons": None,
            }
        ],
        "description": "The original project description.",
    }
    advisor = MagicMock()
    advisor.generate_description = AsyncMock(
        return_value="Build the API and learn service design. Practice persistence patterns."
    )
    project_repo = MagicMock()
    project_repo.get_project_for_regeneration.return_value = project
    project_repo.update_description.return_value = {
        **project,
        "description": advisor.generate_description.return_value,
    }

    service = ProjectGeneratorService(advisor, MagicMock(), project_repo)

    result = await service.regenerate_description(7)

    assert result.id == 7
    assert result.programming_language == "Python"
    assert result.technologies == "FastAPI"
    assert result.addons == "PostgreSQL"
    assert result.level == 3
    assert [extra.model_dump() for extra in result.extras] == project["extras"]
    assert result.description != project["description"]
    advisor.generate_description.assert_awaited_once_with(project)
    project_repo.update_description.assert_called_once_with(7, result.description)


@pytest.mark.asyncio
async def test_regenerate_description_keeps_previous_on_invalid_response() -> None:
    project = {
        "id": 7,
        "programming_language": "Python",
        "technologies": "FastAPI",
        "addons": "PostgreSQL",
        "level": 3,
        "extras": [],
        "description": "The original project description.",
    }
    advisor = MagicMock()
    advisor.generate_description = AsyncMock(return_value="same")
    project_repo = MagicMock()
    project_repo.get_project_for_regeneration.return_value = project

    service = ProjectGeneratorService(advisor, MagicMock(), project_repo)

    result = await service.regenerate_description(7)

    assert result.description == project["description"]
    project_repo.update_description.assert_not_called()


@pytest.mark.asyncio
async def test_regenerate_description_rejects_missing_project_before_ai() -> None:
    advisor = MagicMock()
    advisor.generate_description = AsyncMock()
    project_repo = MagicMock()
    project_repo.get_project_for_regeneration.return_value = None
    service = ProjectGeneratorService(advisor, MagicMock(), project_repo)

    with pytest.raises(ValueError, match="Project not found"):
        await service.regenerate_description(99)

    advisor.generate_description.assert_not_awaited()


@pytest.mark.asyncio
async def test_regenerate_description_uses_fallback_when_ai_fails() -> None:
    project = {
        "id": 7,
        "programming_language": "Python",
        "technologies": "FastAPI",
        "addons": "PostgreSQL",
        "level": 3,
        "extras": [],
        "description": "The original project description.",
    }
    advisor = MagicMock()
    advisor.generate_description = AsyncMock(side_effect=RuntimeError("offline"))
    project_repo = MagicMock()
    project_repo.get_project_for_regeneration.return_value = project
    project_repo.update_description.side_effect = lambda _, description: {
        **project,
        "description": description,
    }
    service = ProjectGeneratorService(advisor, MagicMock(), project_repo)

    result = await service.regenerate_description(7)

    assert result.description != project["description"]
    assert len(result.description) < 400
    project_repo.update_description.assert_called_once()
