from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/ensable_project", tags=["ensable_project"])


class GenerateProjectRequest(BaseModel):
    programming_language: str
    technologies: list[str] = []
    addons: list[str] = []


@router.post("/generate")
async def generate_project(payload: GenerateProjectRequest):
    project = {
        "name": "Generated Project",
        "programming_language": payload.programming_language,
        "technologies": payload.technologies,
        "addons": payload.addons,
    }

    return project
