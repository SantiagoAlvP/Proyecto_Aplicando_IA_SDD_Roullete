import { Reel } from "./Reel";
import type { CatalogEntry, ExcludedCatalog, ExcludableReelKey, ReelKey, ReelsState } from "../types";

interface SlotMachineProps {
  reels: ReelsState;
  catalog: Record<ReelKey, CatalogEntry[]>;
  allCatalog: Record<ReelKey, CatalogEntry[]>;
  excluded: ExcludedCatalog;
  level: number;
  spinning: boolean;
  catalogReady: boolean;
  catalogLoaded: boolean;
  onToggleLock: (key: ReelKey) => void;
  onChangeReel: (key: ReelKey, value: string) => void;
  onChangeLevel: (level: number) => void;
  onToggleExclude: (key: ExcludableReelKey, value: string) => void;
  onClearExcluded: () => void;
  onSpin: () => void;
}

const REELS: { key: ReelKey; label: string }[] = [
  { key: "programming_language", label: "Lenguaje" },
  { key: "technologies", label: "Tecnología" },
  { key: "addons", label: "Addon" },
];

const EXCLUDABLE_REELS: { key: ExcludableReelKey; label: string }[] = [
  { key: "programming_language", label: "Lenguaje" },
  { key: "technologies", label: "Tecnología" },
];

export function SlotMachine({
  reels,
  catalog,
  allCatalog,
  excluded,
  level,
  spinning,
  catalogReady,
  catalogLoaded,
  onToggleLock,
  onChangeReel,
  onChangeLevel,
  onToggleExclude,
  onClearExcluded,
  onSpin,
}: SlotMachineProps) {
  return (
    <section className="machine" aria-label="Máquina tragamonedas">
      <div className="machine__reels">
        {REELS.map(({ key, label }) => (
          <Reel
            key={key}
            label={label}
            state={reels[key]}
            options={catalog[key].map((entry) => entry.name)}
            spinning={spinning && !reels[key].locked}
            disabled={spinning || !catalogReady}
            onToggleLock={() => onToggleLock(key)}
            onChange={(value) => onChangeReel(key, value)}
          />
        ))}
      </div>

      <div className="machine__controls">
        <label className="level">
          <span className="level__label">Dificultad</span>
          <input
            type="range"
            min={1}
            max={5}
            step={1}
            value={level}
            disabled={spinning}
            onChange={(event) => onChangeLevel(Number(event.target.value))}
          />
          <span className="level__value">{level}</span>
        </label>

        <button
          type="button"
          className="spin"
          onClick={onSpin}
          /* Blocking while a request is in flight is what stops a double click
             from spending two LLM calls (HU-07, T016). */
          disabled={spinning || !catalogReady}
        >
          {spinning
            ? "Girando…"
            : !catalogLoaded
              ? "Cargando…"
              : catalogReady
                ? "¡Girar!"
                : "Retira una exclusión"}
        </button>
      </div>

      {catalogLoaded && !catalogReady && (
        <p className="machine__filter-warning" role="status">
          Necesitas dejar al menos un lenguaje y una tecnología disponibles.
        </p>
      )}

      <div className="machine__filters" aria-label="Filtros de exclusión">
        <div className="machine__filters-header">
          <strong>Excluir</strong>
          <button type="button" onClick={onClearExcluded} disabled={spinning}>
            Limpiar
          </button>
        </div>

        {EXCLUDABLE_REELS.map(({ key, label }) => (
          <div key={key} className="machine__filter-group">
            <div className="machine__filter-label">{label}</div>
            <div className="machine__filter-list">
              {allCatalog[key].length === 0 && <span className="machine__filter-empty">Sin opciones disponibles</span>}
              {allCatalog[key].map(({ name }) => {
                const blocked = excluded[key].includes(name);
                return (
                  <button
                    key={name}
                    type="button"
                    className={blocked ? "machine__filter-chip machine__filter-chip--blocked" : "machine__filter-chip"}
                    onClick={() => onToggleExclude(key, name)}
                    disabled={spinning}
                  >
                    {name}
                  </button>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
