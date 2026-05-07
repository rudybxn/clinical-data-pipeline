import copy

# Per schema version, each entity type gets specific field renames and restructuring.
# The generator always produces canonical format; this module converts to clinic format.
#
# v1 (older EHR):  patient_dob, flat address, OV, provider_npi, result_status, M/F gender
# v2 (modern):     canonical field names, Male/Female gender
# v3 (hybrid):     birthdate, mixed address, outpatient, npi_number, lab_status, male/female


_GENDER_MAP = {
    "v1": {"M": "M", "F": "F"},
    "v2": {"M": "Male", "F": "Female"},
    "v3": {"M": "male", "F": "female"},
}


def _drift_patient(record: dict, version: str) -> dict:
    gender = record.get("gender")
    if gender in _GENDER_MAP.get(version, {}):
        record["gender"] = _GENDER_MAP[version][gender]

    if version == "v1":
        if "date_of_birth" in record:
            record["patient_dob"] = record.pop("date_of_birth")
        if isinstance(record.get("address"), dict):
            addr = record.pop("address")
            record["address_street"] = addr.get("street")
            record["address_city"] = addr.get("city")
            record["address_state"] = addr.get("state")
            record["address_zip"] = addr.get("zip")

    elif version == "v3":
        if "date_of_birth" in record:
            record["birthdate"] = record.pop("date_of_birth")
        if isinstance(record.get("address"), dict):
            addr = record.pop("address")
            # Street is flattened; city/state/zip stay nested
            record["address_street"] = addr.get("street")
            record["address"] = {
                "city": addr.get("city"),
                "state": addr.get("state"),
                "zip": addr.get("zip"),
            }

    return record


def _drift_encounter(record: dict, version: str) -> dict:
    type_map = {"v1": "OV", "v2": "OFFICE_VISIT", "v3": "outpatient"}
    if "encounter_type" in record:
        record["encounter_type"] = type_map.get(version, record["encounter_type"])
    return record


def _drift_provider(record: dict, version: str) -> dict:
    if version == "v1" and "npi" in record:
        record["provider_npi"] = record.pop("npi")
    elif version == "v3" and "npi" in record:
        record["npi_number"] = record.pop("npi")
    return record


def _drift_lab_result(record: dict, version: str) -> dict:
    if version == "v1" and "status" in record:
        record["result_status"] = record.pop("status")
    elif version == "v3" and "status" in record:
        record["lab_status"] = record.pop("status")
    return record


_DRIFTERS = {
    "patient": _drift_patient,
    "encounter": _drift_encounter,
    "provider": _drift_provider,
    "lab_result": _drift_lab_result,
}


def apply_schema_drift(record: dict, schema_version: str, entity_type: str) -> dict:
    record = copy.deepcopy(record)
    drifter = _DRIFTERS.get(entity_type)
    if drifter:
        record = drifter(record, schema_version)
    return record
