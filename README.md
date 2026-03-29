# Soundmining Monorepo

A unified, machine-agnostic ecosystem for **SuperCollider** synthesis, **Reaper** orchestration, and **Python**-driven metadata management.

---

## Tech Stack & Tooling

This repository is built on a modern Python stack designed for speed and portability:

* **Package Manager:** [uv](https://github.com/astral-sh/uv) (Extremely fast Rust-based replacement for pip/venv)
* **Build System:** [Hatchling](https://hatch.pypa.io/) (Used for all internal libraries in `lib/`)
* **Linter/Formatter:** [Ruff](https://docs.astral.sh/ruff/) (Instant code cleanup and import sorting)
* **Editor:** [Visual Studio Code](https://code.visualstudio.com/) (Optimized via `.code-workspace`)

---

## Repository Structure

```text
.
├── lib/                 # Shared internal Python packages (Editable)
│   └── soundmining_lib/ # The common soundmining composing library
├── tools/               # Automation scripts
├── projects/            # Individual musical pieses and projects
├── .venv/               # Single unified virtual environment (managed by uv)
└── soundmining.code-workspace  # The master VS Code view
```

# 1. Getting Started
With homebrew installed run:

```bash
brew install uv
```

# 2. Init the environment
In the root of the monorepo, run the following
```bash
uv sync
```

# 3. Opening the Workspace
Opening the monorepo in VS Code.

1. Open VS Code.
2. Go to File > Open Workspace from File...
3. Select soundmining.code-workspace


