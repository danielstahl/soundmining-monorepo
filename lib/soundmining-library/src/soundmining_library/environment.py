from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class ProjectEnvironment:
    sound_path: Path
    synth_defs: Path


def find_git_root() -> Path:
    current = Path.cwd().resolve()
    # Check current and all parent directories
    for parent in [current] + list(current.parents):
        if (parent / ".git").exists():
            return parent
    raise FileNotFoundError("Could not find the monorepo root (no .git folder found).")


def resolve_project_environment() -> ProjectEnvironment:
    # Initialize Paths
    repo_root = find_git_root()
    project_dir = Path.cwd().resolve()

    with open(repo_root / "config.yaml", "r") as f:
        root_cfg = yaml.safe_load(f)
        # Using .get() prevents crashes if keys are missing
        base_sound_path = Path(root_cfg.get("roots", {}).get("sounds", ""))
        synthdefs_path = Path(root_cfg.get("synthdefs", ""))

    # 2. Load Project Config (Relative extension)
    # This assumes config.yaml is in the same folder as the notebook
    with open(project_dir / "config.yaml", "r") as f:
        project_cfg = yaml.safe_load(f)
        rel_sound_path = project_cfg.get("paths", {}).get("sounds", "")

    # 3. Resolve Final Path
    full_audio_path = (base_sound_path / rel_sound_path).resolve()

    return ProjectEnvironment(full_audio_path, synthdefs_path)
