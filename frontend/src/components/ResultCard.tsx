import { ShareButton } from "./ShareButton";
import type { Project } from "../types";

interface ResultCardProps {
  project: Project;
}

function describeExtra(extra: Project["extras"][number]): string {
  return [extra.programming_language, extra.technologies, extra.addons]
    .filter(Boolean)
    .join(" · ");
}

export function ResultCard({ project }: ResultCardProps) {
  const extras = project.extras.map(describeExtra).filter((text) => text.length > 0);

  return (
    <article className="result">
      <header className="result__header">
        <h2 className="result__title">
          {project.technologies} en {project.programming_language}
        </h2>
        <span className="result__level">Nivel {project.level}</span>
      </header>

      <p className="result__description">{project.description}</p>

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

      <ShareButton token={project.share_token} />
    </article>
  );
}
