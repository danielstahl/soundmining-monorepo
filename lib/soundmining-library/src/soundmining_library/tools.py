import subprocess
from pathlib import Path

from soundmining_library.environment import ProjectEnvironment


class Tools:
    def __init__(self, project_environment: ProjectEnvironment) -> None:
        self._environment = project_environment

    def run_nrt_render(self, score_path: Path, output_path: Path, num_channels: int):
        sclang_path = str(self._environment.sclang_path)
        render_nrt_path = str(self._environment.render_nrt_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        command = [
            sclang_path,
            render_nrt_path,
            str(score_path),
            str(output_path),
            str(num_channels),
        ]

        result = subprocess.run(command, capture_output=True, text=True)

        print(result.stdout)

        if result.returncode != 0:
            raise RuntimeError(f"sclang exited with code {result.returncode}:\n{result.stderr}")

        if "RENDER_COMPLETE" not in result.stdout:
            raise RuntimeError(f"NRT render failed:\n{result.stdout}")
