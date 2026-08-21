import { Reel } from "./Reel";
import type { CatalogEntry, ReelKey, ReelsState } from "../types";

interface SlotMachineProps {
  reels: ReelsState;
  catalog: Record<ReelKey, CatalogEntry[]>;
  level: number;
  spinning: boolean;
  catalogReady: boolean;
  onToggleLock: (key: ReelKey) => void;
  onChangeReel: (key: ReelKey, value: string) => void;
  onChangeLevel: (level: number) => void;
  onSpin: () => void;
}

const REELS: { key: ReelKey; label: string }[] = [
  { key: "programming_language", label: "Lenguaje" },
  { key: "technologies", label: "Tecnología" },
  { key: "addons", label: "Addon" },
];

export function SlotMachine({
  reels,
  catalog,
  level,
  spinning,
  catalogReady,
  onToggleLock,
  onChangeReel,
  onChangeLevel,
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
          {spinning ? "Girando…" : catalogReady ? "¡Girar!" : "Cargando…"}
        </button>
      </div>
    </section>
  );
}
