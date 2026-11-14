import json
from pathlib import Path

from app.main import app


def main() -> None:
    contract_path = Path(__file__).resolve().parents[1] / "api" / "openapi.json"
    contract_path.parent.mkdir(parents=True, exist_ok=True)
    contract_path.write_text(
        json.dumps(app.openapi(), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {contract_path}")


if __name__ == "__main__":
    main()
