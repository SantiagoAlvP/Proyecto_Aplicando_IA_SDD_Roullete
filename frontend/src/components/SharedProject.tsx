import { useEffect, useState } from "react";

import { api } from "../api";
import type { SharedProject as SharedProjectData } from "../types";

interface SharedProjectProps {
  token: string;
}

type LoadState =
  | { status: "loading" }
  | { status: "ready"; project: SharedProjectData }
  | { status: "unavailable" };

// Same contract the API enforces at its edge. A token failing this check can
// only come from a mangled or manipulated link, so there is nothing to ask
// the server: we answer with the friendly page straight away (HU-20, FR-008).
const SHARE_TOKEN = /^[A-Za-z0-9_-]{10,64}$/;

export function SharedProject({ token }: SharedProjectProps) {
  const [state, setState] = useState<LoadState>({ status: "loading" });

  useEffect(() => {
    if (!SHARE_TOKEN.test(token)) {
      setState({ status: "unavailable" });
      return;
    }

    let cancelled = false;

    setState({ status: "loading" });
    api
      .sharedProject(token)
      .then((project) => {
        if (!cancelled) setState({ status: "ready", project });
      })
      .catch(() => {
        // 404 or network failure read exactly the same to a visitor; neither
        // may surface technical detail (US3).
        if (!cancelled) setState({ status: "unavailable" });
      });

    return () => {
      cancelled = true;
    };
  }, [token]);

  return (
    <div className="page shared-page">
      <header className="page__header">
        <h1 className="page__title">
          Project <span className="page__title-accent">Jackpot</span>
        </h1>
        <p className="page__subtitle">
          Un proyecto generado en la máquina tragamonedas de ideas.
        </p>
      </header>

      <main className="page__main shared-page__main">
        {state.status === "loading" && (
          <p className="placeholder">Abriendo el proyecto…</p>
        )}

        {state.status === "ready" && (
          <SharedCard project={state.project} />
        )}

        {state.status === "unavailable" && (
          <article className="result shared-page__card">
            <h2 className="shared-page__missing-title">
              Proyecto no disponible
            </h2>
            <p className="result__description">
              El enlace no corresponde a ningún proyecto publicado. Puede que
              se haya cortado al copiarlo.
            </p>
            <a className="shared-page__cta" href="/">
              Gira tu propio proyecto en la máquina
            </a>
          </article>
        )}
      </main>
    </div>
  );
}

function describeExtra(extra: SharedProjectData["extras"][number]): string {
  return [extra.programming_language, extra.technologies, extra.addons]
    .filter(Boolean)
    .join(" · ");
}

function SharedCard({ project }: { project: SharedProjectData }) {
  const extras = project.extras.map(describeExtra).filter((text) => text.length > 0);

  return (
    <article className="result shared-page__card">
      <header className="result__header">
        <h2 className="result__title">
          {project.technologies} en {project.programming_language}
        </h2>
        <span className="result__level">
          {project.level === null ? "Nivel no registrado" : `Nivel ${project.level}`}
        </span>
      </header>

      <div className="shared-page__description">
        <p className="result__description">{project.description}</p>
      </div>

      <dl className="result__facts">
        <div>
          <dt>Lenguaje</dt>
          <dd>{project.programming_language}</dd>
        </div>
        <div>
          <dt>Tecnología</dt>
          <dd>{project.technologies}</dd>
        </div>
        <div>
          <dt>Addon</dt>
          <dd>{project.addons}</dd>
        </div>
      </dl>

      {extras.length > 0 && (
        <div className="result__extras">
          <h3>Restricciones extra</h3>
          <ul>
            {extras.map((extra, index) => (
              <li key={`${extra}-${index}`}>{extra}</li>
            ))}
          </ul>
        </div>
      )}

      <a className="shared-page__cta" href="/">
        Crea el tuyo en la máquina tragamonedas
      </a>
    </article>
  );
}
