import uuid
import csv
import random
from datetime import datetime, timezone, timedelta
from pathlib import Path

_DATA_DIR = Path(__file__).parent.parent / "data"

_LOINC_TESTS: list[dict] = []
with open(_DATA_DIR / "loinc_codes.csv") as f:
    for row in csv.DictReader(f):
        _LOINC_TESTS.append({
            "code": row["code"],
            "name": row["name"],
            "unit": row["unit"],
            "ref_low": float(row["ref_low"]),
            "ref_high": float(row["ref_high"]),
        })


def _generate_value(ref_low: float, ref_high: float) -> float:
    midpoint = (ref_low + ref_high) / 2
    spread = (ref_high - ref_low) * 0.8
    value = random.gauss(midpoint, spread / 2)
    return round(max(0.0, value), 1)


def generate_lab_result(patient_id: str, encounter_id: str, clinic_id: str) -> dict:
    test = random.choice(_LOINC_TESTS)
    result_date = datetime.now() - timedelta(days=random.randint(0, 365))

    return {
        "lab_id": str(uuid.uuid4()),
        "patient_id": patient_id,
        "encounter_id": encounter_id,
        "loinc_code": test["code"],
        "test_name": test["name"],
        "value": _generate_value(test["ref_low"], test["ref_high"]),
        "unit": test["unit"],
        "reference_range_low": test["ref_low"],
        "reference_range_high": test["ref_high"],
        "result_date": result_date.date().isoformat(),
        "status": "final",
        "source_clinic": clinic_id,
        "ingestion_timestamp": datetime.now(timezone.utc).isoformat(),
    }
