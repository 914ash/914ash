import json
from pathlib import Path

from .service import evaluate_payload


def main() -> None:
    payload_path = Path("demo_project/sample_payload.json")
    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    result = evaluate_payload(payload)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
