import json
import os
from datetime import datetime


def write_records(records: list[dict], clinic_id: str, entity_type: str, output_dir: str) -> str:
    clinic_dir = os.path.join(output_dir, clinic_id)
    os.makedirs(clinic_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(clinic_dir, f"{entity_type}_{timestamp}.jsonl")

    with open(filepath, "w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    return filepath
