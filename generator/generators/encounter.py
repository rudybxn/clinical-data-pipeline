import uuid
import random
from datetime import datetime, timezone, timedelta
from pathlib import Path

_DATA_DIR = Path(__file__).parent.parent / "data"

with open(_DATA_DIR / "icd10_codes.txt") as f:
    ICD10_CODES = [l.strip() for l in f if l.strip() and not l.startswith("#")]

with open(_DATA_DIR / "cpt_codes.txt") as f:
    CPT_CODES = [l.strip() for l in f if l.strip() and not l.startswith("#")]


def generate_encounter(patient_id: str, provider_id: str, clinic_id: str) -> dict:
    encounter_date = datetime.now() - timedelta(days=random.randint(0, 365))
    num_diagnoses = random.choices([1, 2, 3], weights=[0.6, 0.3, 0.1])[0]
    num_procedures = random.choices([0, 1, 2], weights=[0.3, 0.55, 0.15])[0]

    return {
        "encounter_id": str(uuid.uuid4()),
        "patient_id": patient_id,
        "provider_id": provider_id,
        "encounter_date": encounter_date.date().isoformat(),
        "encounter_type": "OFFICE_VISIT",
        "diagnoses": random.sample(ICD10_CODES, k=num_diagnoses),
        "procedures": random.sample(CPT_CODES, k=num_procedures) if num_procedures else [],
        "chief_complaint": random.choice([
            "Annual wellness visit", "Follow-up", "Acute illness", "Medication review",
            "Chronic disease management", "Preventive care", "New symptoms",
        ]),
        "source_clinic": clinic_id,
        "ingestion_timestamp": datetime.now(timezone.utc).isoformat(),
    }
