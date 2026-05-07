import uuid
import random
from datetime import datetime, timezone
from faker import Faker

fake = Faker()

SPECIALTIES = [
    "Family Medicine", "Internal Medicine", "Pediatrics", "Obstetrics & Gynecology",
    "Cardiology", "Dermatology", "Orthopedics", "Psychiatry", "Neurology",
    "Gastroenterology", "Pulmonology", "Endocrinology", "Urgent Care",
]


def _luhn_checksum(number: str) -> int:
    digits = [int(d) for d in reversed(number)]
    total = 0
    for i, d in enumerate(digits):
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return total % 10


def generate_valid_npi() -> str:
    base = [random.randint(0, 9) for _ in range(9)]
    partial = "80840" + "".join(str(d) for d in base)
    for check in range(10):
        if _luhn_checksum(partial + str(check)) == 0:
            return "".join(str(d) for d in base) + str(check)
    return "".join(str(d) for d in base) + "0"


def generate_provider(clinic_id: str) -> dict:
    return {
        "provider_id": str(uuid.uuid4()),
        "npi": generate_valid_npi(),
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "specialty": random.choice(SPECIALTIES),
        "clinic_id": clinic_id,
        "source_clinic": clinic_id,
        "ingestion_timestamp": datetime.now(timezone.utc).isoformat(),
    }
