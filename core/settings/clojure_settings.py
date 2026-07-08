"""
Bridges the Python side of the app to the Clojure implementation of the
ensemble-project AI gateway (core/ai_gateway/ollama_provider.clj and
core/ensemble_project/ensemble_project_ai_gatway_service.clj).

Usage — swap the pure-Python gateway for the Clojure-backed one wherever
it's constructed, e.g. in the FastAPI dependency:

    # core/ensemble_project/api/ensemble_project_router.py
    from core.settings.clojure_settings import ClojureProjectGeneratorAIGateway

    def get_project_service(db: Session = Depends(get_db)) -> ProjectGeneratorService:
        ai_gateway = ClojureProjectGeneratorAIGateway()   # was: ProjectGeneratorAIGateway()
        ...

Requirements on the host running this:
  - the `clojure` CLI installed and on PATH (used to resolve `clojure -Spath`)
  - a deps.edn reachable from CLOJURE_PROJECT_ROOT declaring clj-http +
    cheshire (the one already in the repo works as-is)
  - jpype1 installed on the Python side (`pip install jpype1 --break-system-packages`)

All data crossing the Python <-> Clojure boundary is passed as JSON strings
(see the .clj files) rather than hand-converted jpype objects — this keeps
the interop layer small and avoids brittle Java-collection walking.
"""

import asyncio
import json
import os
import subprocess
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import jpype

from core.ensemble_project.api.ensemble_project_models import ProjectSelection
from core.settings.default import AppSettings


@dataclass
class ClojureSettings:
    """
    Configuration needed to bridge into the Clojure/JVM side of the
    ensemble-project AI gateway.

    CLOJURE_PROJECT_ROOT must point at the directory that contains the
    project's `deps.edn` (the file declaring clj-http / cheshire / etc).
    Defaults to the repo root two levels up from this file
    (.../core/settings/clojure_settings.py -> repo root).
    """

    CLOJURE_PROJECT_ROOT: str = os.environ.get(
        "CLOJURE_PROJECT_ROOT",
        str(Path(__file__).resolve().parents[2]),
    )
    ENSEMBLE_AI_GATEWAY_NS: str = os.environ.get(
        "CLOJURE_ENSEMBLE_AI_GATEWAY_NS",
        "core.ensemble-project.ensemble-project-ai-gatway-service",
    )
    OLLAMA_HOST: str = os.environ.get("OLLAMA_HOST", AppSettings().OLLAMA_HOST)
    OLLAMA_MODEL: str = os.environ.get("OLLAMA_MODEL", AppSettings().OLLAMA_MODEL)


class ClojureBridge:
    """
    Process-wide singleton that boots the JVM once, requires the Clojure
    namespace used by the ensemble-project feature, and exposes its public
    functions (`choose-valid-project`, `generate-description`) as plain,
    blocking Python callables.
    """

    _instance: Optional["ClojureBridge"] = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
        return cls._instance

    def __init__(self, settings: Optional[ClojureSettings] = None):
        if self._initialized:
            return
        self.settings = settings or ClojureSettings()
        self._start_jvm()
        self._require_namespace()
        self._initialized = True

    def _build_classpath(self) -> str:
        result = subprocess.run(
            ["clojure", "-Spath"],
            capture_output=True,
            text=True,
            check=True,
            cwd=self.settings.CLOJURE_PROJECT_ROOT,
        )
        return result.stdout.strip()

    def _start_jvm(self) -> None:
        if jpype.isJVMStarted():
            return
        classpath = self._build_classpath()
        jpype.startJVM(classpath=[classpath])

    def _require_namespace(self) -> None:
        clojure = jpype.JClass("clojure.java.api.Clojure")
        require_fn = clojure.var("clojure.core", "require")
        require_fn.invoke(clojure.read(self.settings.ENSEMBLE_AI_GATEWAY_NS))

        ns = self.settings.ENSEMBLE_AI_GATEWAY_NS
        self._choose_valid_project = clojure.var(ns, "choose-valid-project")
        self._generate_description = clojure.var(ns, "generate-description")

    def choose_valid_project(self, projects: list) -> dict:
        """Blocking call: -> {"best_index": int, "valid": bool, "reason": str | None}"""
        projects_json = json.dumps(projects)
        result = self._choose_valid_project.invoke(
            self.settings.OLLAMA_HOST,
            self.settings.OLLAMA_MODEL,
            projects_json,
        )
        if result is None:
            raise ValueError(
                "Clojure selector did not return a structured selection result"
            )
        return json.loads(str(result))

    def generate_description(self, project: dict) -> str:
        """Blocking call: -> plain-text description string."""
        project_json = json.dumps(project)
        result = self._generate_description.invoke(
            self.settings.OLLAMA_HOST,
            self.settings.OLLAMA_MODEL,
            project_json,
        )
        return str(result).strip() if result is not None else ""


class ClojureProjectGeneratorAIGateway:
    """
    Drop-in, Clojure-backed replacement for
    core.ensemble_project.ensemble_project_ai_gatway_service.ProjectGeneratorAIGateway.

    Keeps the exact same async public interface (`choose_valid_project`,
    `generate_description`) so it can be swapped in anywhere a
    ProjectGeneratorAIGateway is expected. The underlying JVM call is
    blocking, so it's pushed onto the default executor to keep the async
    event loop free.
    """

    def __init__(self, settings: Optional[ClojureSettings] = None):
        self._bridge = ClojureBridge(settings)

    async def choose_valid_project(self, projects: list[dict]) -> ProjectSelection:
        loop = asyncio.get_event_loop()
        raw = await loop.run_in_executor(
            None, self._bridge.choose_valid_project, projects
        )
        return ProjectSelection(**raw)

    async def generate_description(self, project: dict) -> str:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self._bridge.generate_description, project
        )
