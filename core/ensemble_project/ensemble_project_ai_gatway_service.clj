(ns core.ensemble-project.ensemble-project-ai-gatway-service
  "Clojure counterpart of
   core.ensemble_project.ensemble_project_ai_gatway_service.ProjectGeneratorAIGateway.

   Every public function here is deliberately string-in / string-out
   (host + model as plain strings, everything else as JSON) so it can be
   invoked directly from Python over jpype without hand-converting Python
   dict/list objects into Clojure maps/vectors and back. See
   core/settings/clojure_settings.py for the Python-side bridge."
  (:require [core.ai-gateway.ollama-provider :as ollama]
            [cheshire.core :as json]
            [clojure.string :as str]))

(def project-selection-schema
  {:type       "object"
   :properties {:best_index {:type "integer"}
                :valid      {:type "boolean"}
                :reason     {:type ["string" "null"]}}
   :required   ["best_index" "valid"]})

(def selector-system-prompt
  (str/join
   " "
   ["You are a senior software architect evaluating candidate tech stacks"
    "for build FEASIBILITY, not conventionality."
    "A stack is VALID as long as it is technically possible to build the"
    "stated kind of project with those tools — even if the combination is"
    "unusual, hard, low-level, or non-idiomatic for that language."
    "Novelty, difficulty, or an unconventional pairing is NOT a reason to"
    "reject a stack. Only reject a stack if there is a genuine technical"
    "impossibility or a total mismatch between the tools and the goal"
    "(e.g. the language/runtime fundamentally cannot do the required job,"
    "or the 'stack' isn't a stack at all — just an unrelated tool with no"
    "way to build the actual project)."
    "Among the valid candidates, pick the single best one for its stated"
    "skill level."
    "Respond ONLY with JSON matching the required schema – never add extra prose."]))

(def describer-system-prompt
  (str/join
   " "
   ["You are a software project mentor."
    "Write concise, motivating project descriptions in plain text."
    "No lists, no markdown, strictly under 400 characters."]))

(defn- build-candidates-prompt [projects]
  (let [listed (->> projects
                     (map-indexed (fn [i p] (str (inc i) ". " (json/generate-string p))))
                     (str/join "\n"))]
    (str
     "Evaluate the candidate tech stacks below. Each entry includes "
     "programming_language, technologies, addons, level (1=Beginner..5=Expert) "
     "and extras.\n\n"
     "Judge VALIDITY purely on feasibility: can this project actually be built "
     "with these tools, in principle? Unusual, advanced, or creative combos "
     "are still VALID as long as they're possible.\n\n"
     "VALID examples (unusual but buildable):\n"
     "- URL shortener in Prolog (just needs logic + persistence, doable)\n"
     "- Bootloader in Rust (real, common systems-programming use case)\n"
     "- Blockchain toy implementation in Haskell (pure logic, no blocker)\n"
     "- Python+PostgreSQL web app (any level)\n"
     "- Java+Spring Boot service (intermediate/advanced)\n"
     "- Rust+Axum+PostgreSQL API (advanced)\n\n"
     "INVALID examples (genuinely not buildable / not a real stack):\n"
     "- Operating system in pure Python (no runtime-free execution; Python "
     "needs an interpreter/OS underneath it, can't be the OS itself)\n"
     "- Full online shop in COBOL (no viable HTTP/web/e-commerce tooling exists)\n"
     "- Prolog + CI/CD only (CI/CD isn't a project target, there's nothing to build)\n"
     "- COBOL + React Native (no interop path between them for one project)\n\n"
     "Candidates:\n" listed "\n\n"
     "Pick the best_index (1-based) among the FEASIBLE candidates. "
     "If none are feasible, set valid to false and explain why in reason "
     "(reason is required whenever valid is false).")))

(defn- build-description-prompt [project]
  (str
   "Write a concise, motivating description (2-4 sentences, "
   "strictly under 400 characters) for a developer working on:\n"
   "- Language  : " (get project "programming_language") "\n"
   "- Technology: " (get project "technologies") "\n"
   "- Addon     : " (get project "addons") "\n"
   "- Level     : " (get project "level") " (1=Beginner, 5=Expert)\n"
   "- Extras    : " (get project "extras" []) "\n\n"
   "Explain WHAT they will build and WHAT they will learn. "
   "Plain text only – no lists, no markdown."))

(defn choose-valid-project
  "host, model: plain strings identifying the Ollama server/model.
   projects-json: a JSON array of project maps (same shape the Python
   ProjectGeneratorAIGateway.choose_valid_project receives).

   Returns a JSON string: {\"best_index\": int, \"valid\": bool, \"reason\": string|null}
   — the same fields as the Python ProjectSelection model, so the Python
   bridge can do ProjectSelection(**json.loads(result)) directly."
  [^String host ^String model ^String projects-json]
  (let [projects (json/parse-string projects-json)
        prompt   (build-candidates-prompt projects)
        result   (ollama/generate-structured
                  {:host          host
                   :model         model
                   :system-prompt selector-system-prompt
                   :prompt        prompt
                   :schema        project-selection-schema})]
    (when (nil? result)
      (throw (ex-info
              "Selector agent did not return a valid ProjectSelection structured output"
              {:projects projects})))
    (json/generate-string result)))

(defn generate-description
  "host, model: plain strings identifying the Ollama server/model.
   project-json: a JSON object describing a single project (same shape the
   Python ProjectGeneratorAIGateway.generate_description receives).

   Returns a plain-text description string."
  [^String host ^String model ^String project-json]
  (let [project (json/parse-string project-json)
        prompt  (build-description-prompt project)
        result  (ollama/generate-text
                 {:host          host
                  :model         model
                  :system-prompt describer-system-prompt
                  :prompt        prompt})]
    (str/trim (str result))))