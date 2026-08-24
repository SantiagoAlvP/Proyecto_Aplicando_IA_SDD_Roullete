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
  programming_language: string;
  technologies: string;
  addons: string;
  extras: Extra[];
  level: number;
  description: string;
}

export interface HistoryEntry {
  id: number;
  programming_language: string;
  technologies: string;
  addons: string;
  description: string;
}

// Read-only payload behind a share link (HU-20). `level` is null for projects
// created before levels were persisted.
export interface SharedProject {
  share_token: string;
  programming_language: string;
  technologies: string;
  addons: string;
  extras: Extra[];
  level: number | null;
  description: string;
}

export type ReelKey = "programming_language" | "technologies" | "addons";

export interface ReelState {
  value: string;
  locked: boolean;
}

export type ReelsState = Record<ReelKey, ReelState>;
