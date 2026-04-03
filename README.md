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
├── config.yaml          # Global machine-specific settings
└── soundmining.code-workspace  # The master VS Code view
```

## Configuration

The monorepo uses a hierarchical configuration system across two levels of `config.yaml` files:

### 1. Root `config.yaml` (Global)
Located at the monorepo root, this file defines machine-specific paths and application locations:
* **`roots`**: Base directories for assets like `sounds`, `artwork`, and `mixes`.
* **`applications`**: Absolute paths to external tools like `sclang`, `scsynth`, and `reaper`.
* **`synthdefs`**: The path to compiled SuperCollider synth definitions used by all projects.

### 2. Project `config.yaml` (Local)
Located within each project folder (e.g., `projects/concrete-music-15/config.yaml`), this file defines project-specific metadata:
* **`paths`**: Relative sub-paths that extend the global roots (e.g., a project's `sounds` path is appended to the root's `sounds` directory).

This structure allows the codebase to remain portable across different machines while keeping project-specific logic isolated.

---

## SuperCollider Tools

The monorepo includes Python-wrapped tools to manage the SuperCollider environment, located in `tools/sc/`. These are exposed as CLI commands via `uv`.

### 1. Compile Synths
To compile all SuperCollider SynthDefs into the directory specified in your `config.yaml`:
```bash
uv run sc-compile
```
This runs `tools/sc/compile_synths.scd` using `sclang`.

### 2. Launch SuperCollider
To start a SuperCollider server instance with the project's default bus configuration and synth definitions:
```bash
uv run sc-start
```
This launches `sclang` with `tools/sc/startup.scd`. You can override the audio device via environment variables:
```bash
SC_DEVICE="External Headphones" uv run sc-start
```

---

## Development: Adding New Tools

To add a new automation script or tool to the monorepo:

1. **Create the Script**: Place your Python script in the `tools/` directory (or a subdirectory like `tools/my_tool/`).
   - Use `Path(__file__).parents[n]` to resolve paths relative to the monorepo root.
   - For consistency, use a `main()` function as the entry point.

2. **Register the Entry Point**: Add your script to the `[project.scripts]` section in the root `pyproject.toml`:
   ```toml
   [project.scripts]
   my-new-tool = "tools.my_tool.script_name:main"
   ```

3. **Install/Sync**: Run `uv sync` to register the new command in the virtual environment.

4. **Run**: You can now execute your tool from anywhere in the monorepo using:
   ```bash
   uv run my-new-tool
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


