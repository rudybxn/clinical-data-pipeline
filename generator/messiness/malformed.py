import random
from datetime import datetime, timedelta

_IMPOSSIBLE_DATES = ["13/45/2025", "31/02/2025", "00/00/0000", "99-99-9999"]

_BAD_PHONES = ["555-CALL-NOW", "000-000-0000", "not-a-phone", "N/A", ""]

_BAD_ICD10 = ["Z99.999", "X00.000", "A99.9", "ZZZ.ZZZ"]

_BAD_GENDERS = ["unknown", "U", "9", "other", ""]

_NULL_VARIANTS = ["null", "N/A", "NULL", "", "None"]


def _corrupt_date(_: str) -> str:
    strategy = random.choice(["impossible", "future", "garbled"])
    if strategy == "impossible":
        return random.choice(_IMPOSSIBLE_DATES)
    if strategy == "future":
        return (datetime.now() + timedelta(days=random.randint(365, 3650))).date().isoformat()
    return "".join(random.choices("0123456789", k=8))


def _corrupt_phone(_: str) -> str:
    return random.choice(_BAD_PHONES)


def _corrupt_icd10_list(value: list) -> list:
    if not value:
        return value
    corrupted = list(value)
    idx = random.randrange(len(corrupted))
    corrupted[idx] = random.choice(_BAD_ICD10)
    return corrupted


def _corrupt_npi(value: str) -> str:
    if len(value) == 10 and value.isdigit():
        bad_check = str((int(value[-1]) + 1) % 10)
        return value[:-1] + bad_check
    return "1234567890"


def _corrupt_dob_to_impossible_age(_: str) -> str:
    strategy = random.choice(["negative", "ancient"])
    if strategy == "negative":
        return (datetime.now() + timedelta(days=random.randint(1, 3650))).date().isoformat()
    return (datetime.now() - timedelta(days=365 * random.randint(151, 200))).date().isoformat()


def _corrupt_gender(_: str) -> str:
    return random.choice(_BAD_GENDERS)


def _corrupt_value_to_null(_: object) -> str:
    return random.choice(_NULL_VARIANTS)


_CORRUPTORS: dict[str, list[tuple[str, callable]]] = {
    "patient": [
        ("date_of_birth", _corrupt_dob_to_impossible_age),
        ("phone", _corrupt_phone),
        ("gender", _corrupt_gender),
    ],
    "encounter": [
        ("encounter_date", _corrupt_date),
        ("diagnoses", _corrupt_icd10_list),
        ("chief_complaint", _corrupt_value_to_null),
    ],
    "provider": [
        ("npi", _corrupt_npi),
    ],
    "lab_result": [
        ("result_date", _corrupt_date),
        ("value", lambda _: random.choice([-1.0, 99999.9])),
        ("unit", _corrupt_value_to_null),
    ],
}


def apply_malformed(record: dict, entity_type: str, rate: float) -> tuple[dict, bool]:
    if random.random() >= rate:
        return record, False

    candidates = [
        (field, fn)
        for field, fn in _CORRUPTORS.get(entity_type, [])
        if field in record and record[field] is not None
    ]
    if not candidates:
        return record, False

    field, corrupt_fn = random.choice(candidates)
    record[field] = corrupt_fn(record[field])
    return record, True
