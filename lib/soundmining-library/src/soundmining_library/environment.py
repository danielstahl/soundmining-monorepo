from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class ProjectEnvironment:
    sound_path: Path
    synth_defs: Path
    stage_path: Path
    score_path: Path
    scsynth_path: Path
    sclang_path: Path
    reaper_path: Path
    render_nrt_path: Path


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
        base_stage_path = Path(root_cfg.get("roots", {}).get("stage", ""))
        scsynth_path = Path(root_cfg.get("applications", {}).get("scsynth", ""))
        sclang_path = Path(root_cfg.get("applications", {}).get("sclang", ""))
        reaper_path = Path(root_cfg.get("applications", {}).get("reaper", ""))

    # Resolve Paths

    # 2. Load Project Config (Relative extension)
    # This assumes config.yaml is in the same folder as the notebook
    with open(project_dir / "config.yaml", "r") as f:
        project_cfg = yaml.safe_load(f)
        rel_sound_path = project_cfg.get("paths", {}).get("sounds", "")
        rel_stage_path = project_cfg.get("paths", {}).get("stage", "")
        rel_score_path = project_cfg.get("paths", {}).get("score", "")

    # 3. Resolve Final Path
    full_audio_path = (base_sound_path / rel_sound_path).resolve()
    full_stage_path = (base_stage_path / rel_stage_path).resolve()
    full_score_path = (project_dir / rel_score_path).resolve()
    render_nrt_path = (repo_root / Path("tools/render_nrt.scd")).resolve()

    return ProjectEnvironment(
        sound_path=full_audio_path,
        synth_defs=synthdefs_path,
        stage_path=full_stage_path,
        score_path=full_score_path,
        scsynth_path=scsynth_path,
        sclang_path=sclang_path,
        reaper_path=reaper_path,
        render_nrt_path=render_nrt_path,
    )
