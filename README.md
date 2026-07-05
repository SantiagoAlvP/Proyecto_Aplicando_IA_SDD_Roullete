<<<<<<< HEAD
# project_roulette
=======
# 🎰 Project Jackpot

You dont what to code/VibeCode , NO problem

<p align="center">
  <img src="https://github.com/jero98772/project_roulette/blob/dev/docs/pictures/logo_animated.gif?raw=true" alt="Project Jackpot" width="500">
</p>

<p align="center">
Generate unique software project ideas to challenge yourself, learn new technologies, and build an impressive portfolio.
</p>

---

## 🚀 Overview

**Project Jackpot** is an AI-powered project idea generator built with **FastAPI** and **Ollama**.

It creates software engineering project ideas by combining programming languages, technologies, algorithms, design patterns, and difficulty levels into complete project descriptions.

Whether you're following **Build Your Own X**, completing **CodeCrafters** challenges, or simply looking for your next side project, Project Jackpot provides endless inspiration tailored for learning.

Example ideas include:

* Build a distributed cache in Rust
* Create a Url-shorten engine in Prolog
* Develop REST/SOAP APIs in Ruby
* Implement graph algorithms in Go
* Design Boot Loader in Rust

Each generated project includes a detailed description explaining what you will build and the concepts you will practice.

---

# ✨ Features

* 🎲 Generate completely random software project ideas
* 🎯 Generate projects by difficulty level
* 🛠 Generate projects using selected technologies
* 🤖 AI-generated project descriptions
* 📚 Browse available programming languages, technologies, and addons
* ⚡ REST API built with FastAPI
* 🐘 PostgreSQL database
* 🐳 Docker support
* 📖 Interactive API documentation
* 🧪 Comprehensive automated tests

---

# 🏗 Tech Stack

* FastAPI
* PostgreSQL
* SQLModel
* SQLAlchemy
* Pydantic
* Alembic
* Ollama
* Strands
* Docker
* uv

---

# 🚀 Quick Start

## Requirements

* Docker
* Docker Compose

Clone the repository:

```bash
git clone https://github.com/jero98772/project_jackpot.git
cd project_jackpot
```

Start the API and PostgreSQL:

```bash
docker compose up api postgres
```

---

# 📖 API Documentation

After starting the project, the documentation is available at:

Swagger UI

```
http://127.0.0.1:9600/api/docs
```

ReDoc

```
http://127.0.0.1:9600/api/redocs
```

---

# 📚 API Endpoints

## Health

| Method | Endpoint      | Description  |
| ------ | ------------- | ------------ |
| GET    | `/api/health` | Health check |

---

## Catalog

| Method | Endpoint                                       |
| ------ | ---------------------------------------------- |
| GET    | `/api/v1/catalog/programming-languages`        |
| GET    | `/api/v1/catalog/programming-languages/random` |
| GET    | `/api/v1/catalog/technologies`                 |
| GET    | `/api/v1/catalog/technologies/random`          |
| GET    | `/api/v1/catalog/addons`                       |
| GET    | `/api/v1/catalog/addons/random`                |

---

## Project Generator

| Method | Endpoint                                                   | Description                          |
| ------ | ---------------------------------------------------------- | ------------------------------------ |
| POST   | `/api/v1/ensemble_project/generate_project_totally_random` | Generate a completely random project |
| POST   | `/api/v1/ensemble_project/generate_project_by_level`       | Generate by difficulty level         |
| POST   | `/api/v1/ensemble_project/generate_project_by_value`       | Generate using selected technologies |

---

# 🎲 Example Response

```json
{
  "programming_language": "Python",
  "technologies": "REST/SOAP APIs",
  "addons": "pytest",
  "extras": [
    {
      "programming_language": "Clojure",
      "technologies": "Recommendation Engine",
      "addons": "Docker"
    },
    {
      "programming_language": "None",
      "technologies": "GenAI and LLM",
      "addons": "Best Practices"
    }
  ],
  "level": 3,
  "description": "Build a Python application that integrates with REST/SOAP APIs, is fully tested with pytest, and incorporates a Clojure-powered recommendation engine for create projects running in Docker. Enhance the system with GenAI and LLM capabilities, following modern software engineering best practices to create a scalable, maintainable, and production-ready solution."
}
```
<p align="center">
  <img src="https://github.com/jero98772/project_roulette/blob/dev/docs/pictures/meme.png?raw=true" alt="meme" width="500">
</p>

---

# 📂 Project Structure

```text
.
├── alembic/                 # Database migrations
├── core/
│   ├── ai_gateway/          # AI providers
│   ├── catalog/             # Catalog API and services
│   ├── database/            # Database layer
│   ├── ensemble_project/    # Project generation
│   ├── health/              # Health endpoint
│   └── settings/
├── data/                    # Seed data
├── docs/                    # Documentation
├── tests/                   # Unit and integration tests
├── Dockerfile
├── docker-compose.yml
├── project_jackpot.py
└── pyproject.toml
```

---

# 🤝 Contributing

Contributions are welcome.

Before opening a Pull Request, please ensure:

* All tests pass.
* Ruff reports no issues.
* Ty passes without errors.
* New features include appropriate tests.
* Database changes include Alembic migrations when required.

Recommended workflow:

```bash
uv run pytest -v
uv run ruff format
uv run ruff check --fix
uv run ruff check
uv run ty check
```

---


# 📄 License

This project is licensed under the **GNU General Public License v3.0 (GPL-3.0)**.

See the [LICENSE](LICENSE) file for details.
>>>>>>> dev
