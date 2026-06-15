"""Generate the OpenAPI schema as JSON, for consumption by frontend codegen tools."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.main import app  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "output",
        nargs="?",
        type=Path,
        default=Path("openapi.json"),
        help="Path to write the OpenAPI schema to (default: openapi.json)",
    )
    args = parser.parse_args()

    schema = app.openapi()
    args.output.write_text(json.dumps(schema, indent=2))
    print(f"Wrote OpenAPI schema to {args.output}")


if __name__ == "__main__":
    main()
