import argparse
import random
import sys
from pathlib import Path

import yaml

from generators.patient import generate_patient
from generators.encounter import generate_encounter
from generators.provider import generate_provider
from generators.lab_result import generate_lab_result
from messiness.missing import apply_missing
from messiness.malformed import apply_malformed
from messiness.duplicator import generate_duplicates
from messiness.schema_drift import apply_schema_drift
from file_output import write_records


def _apply_messiness_pipeline(
    records: list[dict],
    entity_type: str,
    clinic: dict,
) -> tuple[list[dict], dict]:
    missing_rate = clinic["missing_field_rate"]
    malformed_rate = clinic["malformed_rate"]
    dup_rate = clinic["duplicate_rate"]
    schema_ver = clinic["schema_version"]

    missing_count = 0
    malformed_count = 0

    for i, record in enumerate(records):
        records[i], applied = apply_missing(record, entity_type, missing_rate)
        if applied:
            missing_count += 1
        records[i], applied = apply_malformed(records[i], entity_type, malformed_rate)
        if applied:
            malformed_count += 1

    records_with_dups, dup_count = generate_duplicates(records, dup_rate)
    final = [apply_schema_drift(r, schema_ver, entity_type) for r in records_with_dups]

    base = len(records)
    stats = {
        "base": base,
        "total": len(final),
        "missing": missing_count,
        "missing_rate_actual": missing_count / base if base else 0,
        "missing_rate_target": missing_rate,
        "malformed": malformed_count,
        "malformed_rate_actual": malformed_count / base if base else 0,
        "malformed_rate_target": malformed_rate,
        "duplicates": dup_count,
        "duplicate_rate_actual": dup_count / base if base else 0,
        "duplicate_rate_target": dup_rate,
    }
    return final, stats


def _rate_ok(actual: float, target: float) -> str:
    delta = abs(actual - target)
    # Within 50% relative tolerance for probabilistic rates — expected at small volumes
    return "ok" if delta <= max(target * 0.5, 0.02) else "WARN"


def process_clinic(clinic: dict, output_dir: str) -> None:
    cid = clinic["id"]
    volume = clinic["volume"]
    num_providers = clinic.get("num_providers", 5)
    lab_volume = int(volume * 0.6)

    print(f"\n[{cid}] {clinic['name']}  (schema: {clinic['schema_version']})")
    print(f"  Targets — missing: {clinic['missing_field_rate']:.0%}  "
          f"malformed: {clinic['malformed_rate']:.0%}  "
          f"dup: {clinic['duplicate_rate']:.0%}")

    providers = [generate_provider(cid) for _ in range(num_providers)]
    patients = [generate_patient(cid) for _ in range(volume)]

    patient_ids = [p["patient_id"] for p in patients]
    provider_ids = [p["provider_id"] for p in providers]

    encounters = [
        generate_encounter(random.choice(patient_ids), random.choice(provider_ids), cid)
        for _ in range(volume)
    ]
    encounter_ids = [e["encounter_id"] for e in encounters]

    lab_results = [
        generate_lab_result(random.choice(patient_ids), random.choice(encounter_ids), cid)
        for _ in range(lab_volume)
    ]

    # Providers use schema drift only (no messiness — they're reference data)
    from messiness.schema_drift import apply_schema_drift
    providers_drifted = [
        apply_schema_drift(p, clinic["schema_version"], "provider") for p in providers
    ]

    entity_results = {}
    for entity_type, records in [
        ("patient", patients),
        ("encounter", encounters),
        ("lab_result", lab_results),
    ]:
        final, stats = _apply_messiness_pipeline(records, entity_type, clinic)
        entity_results[entity_type] = (final, stats)

    for entity_type, (final, stats) in entity_results.items():
        path = write_records(final, cid, entity_type, output_dir)
        ok = _rate_ok(stats["missing_rate_actual"], stats["missing_rate_target"])
        print(f"  {entity_type:<12}  {stats['total']:>4} records  "
              f"missing {stats['missing_rate_actual']:.1%}/{stats['missing_rate_target']:.1%} [{ok}]  "
              f"malformed {stats['malformed_rate_actual']:.1%}/{stats['malformed_rate_target']:.1%}  "
              f"dups +{stats['duplicates']}  → {path}")

    write_records(providers_drifted, cid, "providers", output_dir)
    print(f"  {'providers':<12}  {len(providers_drifted):>4} records  (no messiness)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic EHR data for multiple clinics")
    parser.add_argument("--config", default="clinic_profiles.yml", help="Clinic config YAML")
    parser.add_argument("--output", default="./output", help="Output directory")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility")
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Config not found: {config_path}", file=sys.stderr)
        sys.exit(1)

    with open(config_path) as f:
        config = yaml.safe_load(f)

    clinics = config.get("clinics", [])
    print(f"Generating data for {len(clinics)} clinic(s) → {args.output}")

    for clinic in clinics:
        process_clinic(clinic, args.output)

    print("\nDone.")


if __name__ == "__main__":
    main()
