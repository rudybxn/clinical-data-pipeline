import uuid
import random
from datetime import datetime, timezone
from faker import Faker

fake = Faker()

INSURANCE_PROVIDERS = [
    "Blue Cross Blue Shield", "Aetna", "Cigna", "United Health", "Humana",
    "Kaiser Permanente", "Molina Healthcare", "Anthem", "CVS Health", "Medicaid",
]


def generate_patient(clinic_id: str) -> dict:
    dob = fake.date_of_birth(minimum_age=0, maximum_age=89)
    return {
        "patient_id": str(uuid.uuid4()),
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "date_of_birth": dob.isoformat(),
        "gender": random.choice(["M", "F"]),
        "phone": fake.numerify("###-###-####"),
        "email": fake.email(),
        "address": {
            "street": fake.street_address(),
            "city": fake.city(),
            "state": fake.state_abbr(),
            "zip": fake.zipcode(),
        },
        "insurance": {
            "provider": random.choice(INSURANCE_PROVIDERS),
            "member_id": fake.bothify("???#########"),
            "group_id": fake.bothify("GRP####"),
        },
        "source_clinic": clinic_id,
        "ingestion_timestamp": datetime.now(timezone.utc).isoformat(),
    }
