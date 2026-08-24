import { useCallback, useEffect, useRef, useState } from "react";

import { api, ApiError } from "./api";
import { History } from "./components/History";
import { ResultCard } from "./components/ResultCard";
import { SharedProject } from "./components/SharedProject";
import { SlotMachine } from "./components/SlotMachine";
import type {
  CatalogEntry,
  HistoryEntry,
  Project,
  ReelKey,
  ReelsState,
} from "./types";

const SPIN_ANIMATION_MS = 700;

// HU-20 (D-03): exactly one extra route; pathname inspection beats shipping a
// routing library for it. Trailing slashes are tolerated - links get mangled
// by chat apps when copied.
const SHARED_ROUTE = /^\/proyecto\/([^/]+)$/;

function detectSharedToken(pathname: string): string | null {
  const normalized = pathname.replace(/\/+$/, "");
  const match = SHARED_ROUTE.exec(normalized);
  return match ? decodeURIComponent(match[1]) : null;
}

const EMPTY_REELS: ReelsState = {
  programming_language: { value: "", locked: false },
  technologies: { value: "", locked: false },
  addons: { value: "", locked: false },
};

const EMPTY_CATALOG: Record<ReelKey, CatalogEntry[]> = {
  programming_language: [],
  technologies: [],
  addons: [],
};

export default function App() {
  // A share link must land on the public view without touching the machine:
  // the route is decided once, at startup (HU-20, US1).
  const [sharedToken] = useState(() => detectSharedToken(window.location.pathname));
  const [catalog, setCatalog] = useState(EMPTY_CATALOG);
  const [reels, setReels] = useState<ReelsState>(EMPTY_REELS);
  const [level, setLevel] = useState(3);
  const [project, setProject] = useState<Project | null>(null);
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const [spinning, setSpinning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Guards against a second spin slipping through before React re-renders the
  // disabled button - each spin costs an LLM call.
  const inFlight = useRef(false);

  const catalogReady =
    catalog.programming_language.length > 0 &&
    catalog.technologies.length > 0 &&
    catalog.addons.length > 0;

  const refreshHistory = useCallback(async () => {
    try {
      setHistory(await api.history());
    } catch {
      // The history is a convenience; failing to load it must never block the
      // main flow or replace the screen with an error.
    }
  }, []);

  useEffect(() => {
    // A share link renders read-only content: no catalog, no history fetch.
    if (sharedToken !== null) return;

    let cancelled = false;

    (async () => {
      try {
        const [languages, technologies, addons] = await Promise.all([
          api.programmingLanguages(),
          api.technologies(),
          api.addons(),
        ]);
        if (cancelled) return;
        setCatalog({
          programming_language: languages,
          technologies,
          addons,
        });
      } catch (err) {
        if (!cancelled) setError(messageOf(err));
      }
    })();

    void refreshHistory();
    return () => {
      cancelled = true;
    };
  }, [refreshHistory, sharedToken]);

  function toggleLock(key: ReelKey) {
    setReels((current) => ({
      ...current,
      [key]: { ...current[key], locked: !current[key].locked },
    }));
  }

  function changeReel(key: ReelKey, value: string) {
    setReels((current) => ({
      ...current,
      [key]: { value, locked: value !== "" },
    }));
  }

  async function spin() {
    if (inFlight.current) return;
    inFlight.current = true;

    setSpinning(true);
    setError(null);

    const started = Date.now();
    try {
      const anyLocked = (Object.keys(reels) as ReelKey[]).some(
        (key) => reels[key].locked && reels[key].value !== "",
      );

      const result = anyLocked
        ? await api.generateByValue({
            programming_language: lockedValue(reels, "programming_language"),
            technologies: lockedValue(reels, "technologies"),
            addons: lockedValue(reels, "addons"),
            level,
          })
        : await api.generateByLevel(level);

      // Let the reels finish their animation even when the API is instant,
      // otherwise the result appears before the machine looks like it spun.
      await waitRemaining(started, SPIN_ANIMATION_MS);

      setProject(result);
      setReels((current) => ({
        programming_language: applyResult(
          current.programming_language,
          result.programming_language,
        ),
        technologies: applyResult(current.technologies, result.technologies),
        addons: applyResult(current.addons, result.addons),
      }));
      void refreshHistory();
    } catch (err) {
      await waitRemaining(started, SPIN_ANIMATION_MS);
      setError(messageOf(err));
    } finally {
      setSpinning(false);
      inFlight.current = false;
    }
  }

  if (sharedToken !== null) {
    return <SharedProject token={sharedToken} />;
  }

  return (
    <div className="page">
      <header className="page__header">
        <h1 className="page__title">
          Project <span className="page__title-accent">Jackpot</span>
        </h1>
        <p className="page__subtitle">
          Gira los rodillos y llévate una idea de proyecto para construir.
        </p>
      </header>

      <main className="page__main">
        <div className="page__machine">
          <SlotMachine
            reels={reels}
            catalog={catalog}
            level={level}
            spinning={spinning}
            catalogReady={catalogReady}
            onToggleLock={toggleLock}
            onChangeReel={changeReel}
            onChangeLevel={setLevel}
            onSpin={() => void spin()}
          />

          {error && (
            <div className="alert" role="alert">
              <span>{error}</span>
              <button type="button" onClick={() => void spin()} disabled={spinning}>
                Reintentar
              </button>
            </div>
          )}

          {project && !error && <ResultCard project={project} />}

          {!project && !error && !spinning && (
            <p className="placeholder">
              Fija los rodillos que quieras practicar y deja el resto al azar.
            </p>
          )}
        </div>

        <History entries={history} />
      </main>

      <footer className="page__footer">
        Construido con Spec-Driven Development ·{" "}
        <a href="/api/docs">Documentación de la API</a>
      </footer>
    </div>
  );
}

function lockedValue(reels: ReelsState, key: ReelKey): string {
  const reel = reels[key];
  return reel.locked ? reel.value : "";
}

function applyResult(
  reel: ReelsState[ReelKey],
  value: string,
): ReelsState[ReelKey] {
  return reel.locked ? reel : { value, locked: false };
}

function waitRemaining(startedAt: number, minimumMs: number): Promise<void> {
  const remaining = minimumMs - (Date.now() - startedAt);
  if (remaining <= 0) return Promise.resolve();
  return new Promise((resolve) => setTimeout(resolve, remaining));
}

function messageOf(err: unknown): string {
  if (err instanceof ApiError) {
    return err.requestId ? `${err.message} (id: ${err.requestId})` : err.message;
  }
  return "Algo salió mal. Intenta de nuevo.";
}
