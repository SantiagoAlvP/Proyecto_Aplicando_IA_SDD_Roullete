import { ShareButton } from "./ShareButton";
import type { HistoryEntry } from "../types";

interface HistoryProps {
  entries: HistoryEntry[];
}

export function History({ entries }: HistoryProps) {
  return (
    <aside className="history" aria-label="Historial">
      <h2 className="history__title">Últimas ideas</h2>

      {entries.length === 0 ? (
        <p className="history__empty">
          Todavía no hay nada por aquí. Gira para estrenar el historial.
        </p>
      ) : (
        <ul className="history__list">
          {entries.map((entry) => (
            <li key={entry.id} className="history__item">
              <span className="history__combo">
                {entry.technologies} · {entry.programming_language}
              </span>
              <span className="history__addon">{entry.addons}</span>
              <ShareButton token={entry.share_token} label="Compartir enlace" />
            </li>
          ))}
        </ul>
      )}
    </aside>
  );
}
