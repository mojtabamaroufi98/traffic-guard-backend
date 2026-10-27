from datetime import datetime

from memory import load_records
from reports import get_report
from models import TrafficStatus


def get_current_vehicles():
    records = load_records()

    return [
        record
        for record in records
        if record.status == TrafficStatus.INSIDE
    ]


def get_today_records():
    records = load_records()

    today = datetime.now().date()

    return [
        record
        for record in records
        if datetime.fromtimestamp(
            record.entry_time / 1000
        ).date() == today
    ]


def get_traffic_summary():
    records = load_records()

    today = datetime.now().date()

    today_records = [
        record
        for record in records
        if datetime.fromtimestamp(
            record.entry_time / 1000
        ).date() == today
    ]

    entered = len(today_records)

    exited = sum(
        1
        for record in records
        if record.exit_time
        and datetime.fromtimestamp(
            record.exit_time / 1000
        ).date() == today
    )

    inside = sum(
        1
        for record in records
        if record.status == TrafficStatus.INSIDE
    )

    return {
        "today_entered": entered,
        "today_exited": exited,
        "inside_now": inside,
        "total_records": len(records),
    }


def search_vehicle(plate_text: str):
    records = load_records()

    query = plate_text.replace(" ", "").replace("-", "").strip()

    results = []

    for record in records:
        plate = (
            f"{record.plate.two}"
            f"{record.plate.letter}"
            f"{record.plate.three}"
            f"{record.plate.region}"
        )

        if query in plate:
            results.append(record)

    return results


def get_reports_data():
    report = get_report()

    return {
        "daily": [
            item.model_dump()
            for item in report.daily
        ],
        "weekly": [
            item.model_dump()
            for item in report.weekly
        ],
        "monthly": [
            item.model_dump()
            for item in report.monthly
        ],
        "peak_hours": [
            item.model_dump()
            for item in report.peak_hours
        ],
        "top_vehicles": [
            item.model_dump()
            for item in report.top_vehicles
        ],
        "average_stay_minutes": report.avg_stay_minutes,
        "by_type": [
            item.model_dump()
            for item in report.by_type
        ],
    }