import { useCallback, useEffect, useRef, useState } from "react";

import { api, ApiError } from "./api";
import { History } from "./components/History";
import { ResultCard } from "./components/ResultCard";
import { SlotMachine } from "./components/SlotMachine";
import type {
  CatalogEntry,
  HistoryEntry,
  Project,
  ReelKey,
  ReelsState,
} from "./types";

const SPIN_ANIMATION_MS = 700;

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
  const [catalog, setCatalog] = useState(EMPTY_CATALOG);
  const [reels, setReels] = useState<ReelsState>(EMPTY_REELS);
  const [level, setLevel] = useState(3);
  const [project, setProject] = useState<Project | null>(null);
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const [favorites, setFavorites] = useState<HistoryEntry[]>([]);
  const [activeTab, setActiveTab] = useState<"history" | "favorites">("history");
  const [pendingFavoriteId, setPendingFavoriteId] = useState<number | null>(null);
  const [favoriteError, setFavoriteError] = useState<string | null>(null);
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

  const refreshFavorites = useCallback(async () => {
    try {
      setFavorites(await api.favorites());
    } catch {
      // Same convenience guarantee as the history panel.
    }
  }, []);

  useEffect(() => {
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
    void refreshFavorites();
    return () => {
      cancelled = true;
    };
  }, [refreshHistory, refreshFavorites]);

  async function toggleFavorite(entry: { id: number; favorite: boolean }) {
    if (pendingFavoriteId !== null) return;
    setPendingFavoriteId(entry.id);
    setFavoriteError(null);

    try {
      const updated = entry.favorite
        ? await api.unmarkFavorite(entry.id)
        : await api.markFavorite(entry.id);

      setProject((current) =>
        current && current.id === entry.id
          ? { ...current, favorite: updated.favorite }
          : current,
      );
      setHistory((current) =>
        current.map((item) =>
          item.id === entry.id ? { ...item, favorite: updated.favorite } : item,
        ),
      );
      setFavorites((current) =>
        updated.favorite
          ? [updated, ...current.filter((item) => item.id !== entry.id)]
          : current.filter((item) => item.id !== entry.id),
      );
    } catch (err) {
      setFavoriteError(messageOf(err));
    } finally {
      setPendingFavoriteId(null);
    }
  }

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

          {project && !error && (
            <ResultCard
              project={project}
              onToggleFavorite={() => void toggleFavorite(project)}
              favoritePending={pendingFavoriteId === project.id}
            />
          )}

          {favoriteError && (
            <p className="alert alert--inline" role="alert">
              {favoriteError}
            </p>
          )}

          {!project && !error && !spinning && (
            <p className="placeholder">
              Fija los rodillos que quieras practicar y deja el resto al azar.
            </p>
          )}
        </div>

        <div className="page__panel">
          <div className="panel__tabs" role="tablist">
            <button
              type="button"
              role="tab"
              aria-selected={activeTab === "history"}
              className={activeTab === "history" ? "panel__tab panel__tab--active" : "panel__tab"}
              onClick={() => setActiveTab("history")}
            >
              Historial
            </button>
            <button
              type="button"
              role="tab"
              aria-selected={activeTab === "favorites"}
              className={activeTab === "favorites" ? "panel__tab panel__tab--active" : "panel__tab"}
              onClick={() => setActiveTab("favorites")}
            >
              Favoritos
            </button>
          </div>

          {activeTab === "history" ? (
            <History
              title="Últimas ideas"
              entries={history}
              emptyMessage="Todavía no hay nada por aquí. Gira para estrenar el historial."
              onToggleFavorite={(entry) => void toggleFavorite(entry)}
              pendingId={pendingFavoriteId}
            />
          ) : (
            <History
              title="Favoritos"
              entries={favorites}
              emptyMessage="Todavía no marcaste ningún proyecto como favorito."
              onToggleFavorite={(entry) => void toggleFavorite(entry)}
              pendingId={pendingFavoriteId}
            />
          )}
        </div>
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
