from pathlib import Path
import json
import time

from  backend.models import TrafficRecord


DATA_DIR = Path(__file__).parent / "data"
DATA_FILE = DATA_DIR / "traffic.json"


def ensure_data_file():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not DATA_FILE.exists():
        DATA_FILE.write_text("[]", encoding="utf-8")


def load_records() -> list[TrafficRecord]:
    ensure_data_file()

    try:
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []

    return [TrafficRecord.model_validate(item) for item in data]


def save_records(records: list[TrafficRecord]) -> None:
    ensure_data_file()

    data = [
        record.model_dump(mode="json")
        for record in records
    ]

    DATA_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def add_record(record: TrafficRecord) -> TrafficRecord:
    records = load_records()
    records.insert(0, record)
    save_records(records)
    return record


def get_record(record_id: str) -> TrafficRecord | None:
    records = load_records()

    for record in records:
        if record.id == record_id:
            return record

    return None


def update_record(record: TrafficRecord) -> TrafficRecord:
    records = load_records()

    for index, item in enumerate(records):
        if item.id == record.id:
            records[index] = record
            save_records(records)
            return record

    raise ValueError("رکورد مورد نظر پیدا نشد.")


def generate_record_id() -> str:
    return f"T-{int(time.time() * 1000)}"