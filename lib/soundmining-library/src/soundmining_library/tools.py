import subprocess
from pathlib import Path

from soundmining_library.environment import ProjectEnvironment


class Tools:
    def __init__(self, project_environment: ProjectEnvironment) -> None:
        self._environment = project_environment


def run_nrt_render(self, score_path: Path, output_path: Path, num_channels: int):
    sclang_path = str(self._environment.sclang_path)
    render_nrt_path = str(self._environment.render_nrt_path)

    command = [
        sclang_path,
        render_nrt_path,
        str(score_path),
        str(output_path),
        str(num_channels),
    ]
    subprocess.run(command, check=True)
