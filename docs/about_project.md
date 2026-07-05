I want to build an application to learn and practice industry best practices, such as:

    SOLID Principles

    SQLModel (for Async ORM)

    Scalable Architecture Design

    Dependency Injection (cleanly managing service lifetimes)

    API Design (RESTful best practices, clean request/response schemas)

The core idea is to build a simple application intentionally over-engineered to demonstrate these concepts in a production-ready setup.
Tech Stack & Development Environment

    Backend: FastAPI (fully asynchronous).

    Frontend: React.

    Tooling & Quality Assurance: uv for lightning-fast package management, pre-commit hooks, and Ruff for linting and type-checking, along with a robust testing suite (Pytest).

    Infrastructure (Docker-in-Docker): A localized Docker environment running PostgreSQL and Ollama.

    Database Best Practices: PostgreSQL configured with strict data integrity, explicit Foreign Keys, normalization to eliminate data redundancy, and proper indexing.

Core Concept: The Project Idea Jackpot Machine

The application acts as a slot machine that generates tailored project ideas to help developers learn by example.
Example Outputs:

    A distributed Git clone, built in Go (Difficulty: Level 3).

    A Pomodoro application with a decoupled backend/frontend, built in Python and JavaScript (Difficulty: Level 2).

    A bioinformatics-focused filesystem, built in Rust (Difficulty: Level 4).

The "Slot Machine" Reels Mechanics

Initially, the project consists of 3 default reels (slots) that spin to generate a project concept:

    Technology (e.g., Distributed Systems, File Systems, Web App)

    Programming Language (e.g., Go, Python, Rust)

    Core Feature / Focus (e.g., Bioinformatics, Decoupled, Distributed)

    Difficulty Level (e.g., Level 1 to Level 5)

Advanced Customization & Scalability

To truly test the application's scalability and architectural design, the user can customize the randomness by dynamically adding unlimited reels. These extra reels can represent:

    An additional programming language (for multi-language projects).

    An additional technology that must integrate or relate to the first one.

    Extra constraints, features, or architectural patterns that the project must follow.