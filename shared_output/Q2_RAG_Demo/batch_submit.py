"""Package entry point; run the canonical root batch_submit.py from this folder."""
from pathlib import Path
import runpy

runpy.run_path(str(Path(__file__).resolve().parents[2] / "batch_submit.py"), run_name="__main__")
