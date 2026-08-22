// The single network boundary. No component calls fetch directly, so a route
// change or an error-shape change touches exactly one file.

import type { CatalogEntry, HistoryEntry, Project } from "./types";

const BASE = "/api/v1";

export class ApiError extends Error {
  readonly status: number;
  readonly requestId?: string;

  constructor(message: string, status: number, requestId?: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.requestId = requestId;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(path, {
      headers: { "Content-Type": "application/json" },
      ...init,
    });
  } catch {
    // A network failure must read as a network failure, not as a blank screen.
    throw new ApiError(
      "No se pudo contactar el servidor. Revisa tu conexión.",
      0,
    );
  }

  if (!response.ok) {
    throw new ApiError(
      await readErrorMessage(response),
      response.status,
      response.headers.get("X-Request-ID") ?? undefined,
    );
  }

  return (await response.json()) as T;
}

async function readErrorMessage(response: Response): Promise<string> {
  if (response.status === 429) {
    const retry = response.headers.get("Retry-After");
    return retry
      ? `Demasiadas peticiones. Intenta de nuevo en ${retry} segundos.`
      : "Demasiadas peticiones. Espera un momento e intenta de nuevo.";
  }

  try {
    const body = await response.json();
    if (typeof body?.detail === "string") return body.detail;
    if (Array.isArray(body?.errors) && body.errors.length > 0) {
      return `Datos inválidos: ${body.errors[0].message}`;
    }
  } catch {
    // Fall through to the generic message below.
  }
  return `El servidor respondió con un error (${response.status}).`;
}

export const api = {
  programmingLanguages: () =>
    request<CatalogEntry[]>(`${BASE}/catalog/programming-languages`),

  technologies: () => request<CatalogEntry[]>(`${BASE}/catalog/technologies`),

  addons: () => request<CatalogEntry[]>(`${BASE}/catalog/addons`),

  history: (limit = 8) =>
    request<HistoryEntry[]>(`${BASE}/ensemble_project/history?limit=${limit}`),

  favorites: (limit = 50) =>
    request<HistoryEntry[]>(`${BASE}/ensemble_project/favorites?limit=${limit}`),

  markFavorite: (id: number) =>
    request<HistoryEntry>(`${BASE}/ensemble_project/${id}/favorite`, {
      method: "PUT",
    }),

  unmarkFavorite: (id: number) =>
    request<HistoryEntry>(`${BASE}/ensemble_project/${id}/favorite`, {
      method: "DELETE",
    }),

  generateByLevel: (level: number) =>
    request<Project>(`${BASE}/ensemble_project/generate_project_by_level`, {
      method: "POST",
      body: JSON.stringify({ level }),
    }),

  generateByValue: (payload: {
    programming_language: string;
    technologies: string;
    addons: string;
    level: number;
  }) =>
    request<Project>(`${BASE}/ensemble_project/generate_project_by_value`, {
      method: "POST",
      body: JSON.stringify({
        programming_language: payload.programming_language,
        technologies: payload.technologies,
        addons: payload.addons,
        extras: [],
        level: { level: payload.level },
      }),
    }),
};
