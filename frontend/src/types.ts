// Mirrors the backend DTOs in core/ensemble_project/api/ensemble_project_models.py.
// Keeping them in one file means a contract change breaks compilation in one
// place instead of silently at runtime in five components.

export interface CatalogEntry {
  id: number;
  name: string;
}

export interface Extra {
  programming_language: string | null;
  technologies: string | null;
  addons: string | null;
}

export interface Project {
  id: number;
  programming_language: string;
  technologies: string;
  addons: string;
  extras: Extra[];
  level: number;
  description: string;
  favorite: boolean;
}

export interface HistoryEntry {
  id: number;
  programming_language: string;
  technologies: string;
  addons: string;
  level: number | null;
  extras: Extra[];
  description: string;
  favorite: boolean;
}

export type ReelKey = "programming_language" | "technologies" | "addons";

export interface ReelState {
  value: string;
  locked: boolean;
}

export type ReelsState = Record<ReelKey, ReelState>;
