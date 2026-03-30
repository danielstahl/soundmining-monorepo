import subprocess
import sys
from pathlib import Path

import yaml


def load_config(root_dir):
    config_path = root_dir / "config.yaml"
    if not config_path.exists():
        print(f"Warning: config.yaml not found at {config_path}. Using 'sclang' from PATH.")
        return {}
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def main():
    """Entry point for uv run sc-compile"""
    # 1. SETUP PATHS
    # This script is in tools/sc/, so parents[2] is the monorepo root
    root_dir = Path(__file__).parents[2]
    compile_script = root_dir / "tools" / "sc" / "compile_synths.scd"

    config = load_config(root_dir)

    # 2. GET SCLANG PATH
    # Looks in config.yaml -> applications -> sclang
    sclang_path = config.get("applications", {}).get("sclang", "sclang")

    if not compile_script.exists():
        print(f"Error: SuperCollider compiler script not found at {compile_script}")
        sys.exit(1)

    print("Supercollider Synth Compiler")

    # 3. EXECUTE
    # We don't need -p here because we want to see the 0.exit status
    cmd = [sclang_path, str(compile_script)]

    try:
        # run() waits for the process to finish (perfect for a compiler)
        result = subprocess.run(cmd, capture_output=False, text=True)

        if result.returncode == 0:
            print("\nCompilation process finished successfully.")
        else:
            print(f"\nsclang exited with error code: {result.returncode}")

    except FileNotFoundError:
        print(f"Error: Could not find 'sclang' at {sclang_path}. Check config.yaml.")
    except KeyboardInterrupt:
        print("\nAborted by user.")


if __name__ == "__main__":
    main()
