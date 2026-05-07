import random

# Fields that can be set to None, by entity type. Primary keys and metadata are never dropped.
_NULLABLE: dict[str, list[str]] = {
    "patient": ["date_of_birth", "phone", "email", "insurance", "address"],
    "encounter": ["diagnoses", "procedures", "chief_complaint"],
    "provider": ["npi", "specialty"],
    "lab_result": ["reference_range_low", "reference_range_high", "unit"],
}


def apply_missing(record: dict, entity_type: str, rate: float) -> tuple[dict, bool]:
    if random.random() >= rate:
        return record, False

    candidates = [f for f in _NULLABLE.get(entity_type, []) if f in record]
    if not candidates:
        return record, False

    record[random.choice(candidates)] = None
    return record, True
