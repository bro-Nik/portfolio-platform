"""Export the OpenAPI schema to openapi.json without running a server.

Usage (from backend/): python -m app.scripts.export_openapi [output_path]
"""

import json
from pathlib import Path
import sys

from app.main import app


def main() -> None:
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[3] / 'openapi.json'

    schema = app.openapi()
    output.write_text(json.dumps(schema, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
