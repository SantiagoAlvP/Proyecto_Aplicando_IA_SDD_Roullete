import type { HistoryEntry } from "../types";

interface HistoryProps {
  title: string;
  entries: HistoryEntry[];
  emptyMessage: string;
  onToggleFavorite: (entry: HistoryEntry) => void;
  pendingId: number | null;
}

export function History({
  title,
  entries,
  emptyMessage,
  onToggleFavorite,
  pendingId,
}: HistoryProps) {
  return (
    <aside className="history" aria-label={title}>
      <h2 className="history__title">{title}</h2>

      {entries.length === 0 ? (
        <p className="history__empty">{emptyMessage}</p>
      ) : (
        <ul className="history__list">
          {entries.map((entry) => (
            <li key={entry.id} className="history__item">
              <span className="history__combo">
                {entry.technologies} · {entry.programming_language}
              </span>
              <span className="history__addon">{entry.addons}</span>
              <button
                type="button"
                className="favorite-toggle favorite-toggle--small"
                aria-pressed={entry.favorite}
                disabled={pendingId === entry.id}
                onClick={() => onToggleFavorite(entry)}
              >
                {entry.favorite ? "★" : "☆"}
              </button>
            </li>
          ))}
        </ul>
      )}
    </aside>
  );
}
