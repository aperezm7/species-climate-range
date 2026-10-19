"""python -m challenges reveal 03 prints that solution and a short explanation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

CHALLENGES = {
    "01": "01_validate_gbif_point",
    "02": "02_spatial_thinning",
    "03": "03_sample_background",
    "04": "04_roc_auc",
    "05": "05_cell_count_sql",
}


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 2 or args[0] != "reveal":
        print("Usage: python -m challenges reveal NN", file=sys.stderr)
        print("NN is 01, 02, 03, 04, or 05.", file=sys.stderr)
        return 2
    number = args[1].zfill(2)
    slug = CHALLENGES.get(number)
    if slug is None:
        print(f"Unknown challenge {args[1]}. Choose 01 through 05.", file=sys.stderr)
        return 2
    path = ROOT / "hidden" / f"{slug}.py"
    module_name = f"hidden_{slug}"
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        print(f"Missing solution file {path}", file=sys.stderr)
        return 1
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    explanation = getattr(module, "EXPLANATION", "").strip()
    print(f"=== {slug} ===")
    print()
    print(path.read_text(encoding="utf-8").rstrip())
    print()
    print("--- explanation ---")
    print()
    print(explanation or "No explanation was attached to this solution.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
