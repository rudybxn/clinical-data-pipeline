import copy
import random
from datetime import datetime, timezone, timedelta


def generate_duplicates(records: list[dict], rate: float) -> tuple[list[dict], int]:
    duplicates = []
    for record in records:
        if random.random() >= rate:
            continue
        dup = copy.deepcopy(record)
        # Shift ingestion timestamp by a few seconds to minutes — the key dedup challenge
        offset = timedelta(seconds=random.randint(5, 600))
        dup["ingestion_timestamp"] = (
            datetime.now(timezone.utc) + offset
        ).isoformat()
        # For lab results, simulate "ordered then resulted" by upgrading status
        if dup.get("status") == "final":
            dup["status"] = random.choice(["ordered", "preliminary"])
        duplicates.append(dup)

    return records + duplicates, len(duplicates)
