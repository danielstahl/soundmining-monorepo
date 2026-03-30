import os
import subprocess
import sys
from pathlib import Path

import yaml


def load_config():
    # Find the config.yaml at the monorepo root
    root_dir = Path(__file__).parents[2]
    config_path = root_dir / "config.yaml"

    if not config_path.exists():
        print(f"⚠️ Warning: config.yaml not found at {config_path}. Using system defaults.")
        return {}

    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def launch_supercollider():
    config = load_config()
    root_dir = Path(__file__).parents[2]
    sc_script = root_dir / "tools" / "sc" / "startup.scd"

    # 1. GET SCLANG PATH FROM CONFIG
    # Accessing applications -> sclang from the YAML
    sclang_path = config.get("applications", {}).get("sclang", "sclang")

    # 2. ENVIRONMENT VARIABLES
    # Priority: Environment Var > YAML Config > Default String
    device = os.getenv("SC_DEVICE") or config.get("audio", {}).get("default_device", "External Headphones")
    num_outs = os.getenv("SC_NUM_OUTS", "2")

    env = os.environ.copy()
    env["SC_DEVICE"] = device
    env["SC_NUM_OUTS"] = num_outs

    print(f"Starting SuperCollider with device: {device} and num_outs: {num_outs}")

    if "SuperCollider.app" in sclang_path:
        cmd = [sclang_path, str(sc_script)]
    else:
        cmd = [sclang_path, "-p", str(sc_script)]

    try:
        process = subprocess.Popen(
            cmd,
            stdout=sys.stdout,
            stderr=sys.stderr,
            bufsize=1,  # Line buffered
            universal_newlines=True,
        )
        process.wait()
    except FileNotFoundError:
        print(f"❌ Error: Could not find sclang at '{sclang_path}'. Check your config.yaml.")
    except KeyboardInterrupt:
        print("\nStopping SuperCollider")
        process.terminate()


if __name__ == "__main__":
    launch_supercollider()
