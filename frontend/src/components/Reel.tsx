import type { ReelState } from "../types";

interface ReelProps {
  label: string;
  state: ReelState;
  options: string[];
  spinning: boolean;
  disabled: boolean;
  onToggleLock: () => void;
  onChange: (value: string) => void;
}

/**
 * One slot machine reel.
 *
 * A locked reel keeps its value across spins (HU-07, escenario 2), which is
 * how the UI exposes the backend's "fix one value, randomise the rest"
 * behaviour without a second screen.
 */
export function Reel({
  label,
  state,
  options,
  spinning,
  disabled,
  onToggleLock,
  onChange,
}: ReelProps) {
  return (
    <div className={`reel ${state.locked ? "reel--locked" : ""}`}>
      <div className="reel__label">{label}</div>

      <div className={`reel__window ${spinning ? "reel__window--spinning" : ""}`}>
        <span className="reel__value">{state.value || "—"}</span>
      </div>

      <select
        className="reel__select"
        value={state.value}
        disabled={disabled}
        onChange={(event) => onChange(event.target.value)}
        aria-label={`Elegir ${label}`}
      >
        <option value="">Al azar</option>
        {options.map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>

      <button
        type="button"
        className={`reel__lock ${state.locked ? "reel__lock--on" : ""}`}
        onClick={onToggleLock}
        disabled={disabled}
        aria-pressed={state.locked}
      >
        {state.locked ? "Fijado" : "Fijar"}
      </button>
    </div>
  );
}
