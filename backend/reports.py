from datetime import datetime
from collections import Counter

from models import (
    TrafficStatus,
    ReportBundle,
    ChartPoint,
    TopVehicle,
)
from memory import load_records


def _plate_key(plate) -> str:
    return f"{plate.two} {plate.letter} {plate.three} - {plate.region}"


def _timestamp_to_date(timestamp: int):
    return datetime.fromtimestamp(timestamp / 1000).date()


def get_report() -> ReportBundle:
    records = load_records()

    active_records = [
        record
        for record in records
        if record.status != TrafficStatus.CANCELED
    ]

    daily = _build_daily(active_records)
    weekly = _build_weekly(active_records)
    monthly = _build_monthly(active_records)
    peak_hours = _build_peak_hours(active_records)
    top_vehicles = _build_top_vehicles(active_records)
    avg_stay = _calculate_average_stay(active_records)
    by_type = _build_by_type(active_records)

    return ReportBundle(
        daily=daily,
        weekly=weekly,
        monthly=monthly,
        peak_hours=peak_hours,
        top_vehicles=top_vehicles,
        avg_stay_minutes=avg_stay,
        by_type=by_type,
    )


def _build_daily(records) -> list[ChartPoint]:
    result = []

    today = datetime.now().date()

    for offset in range(6, -1, -1):
        target_date = today.fromordinal(today.toordinal() - offset)

        entries = sum(
            1
            for record in records
            if _timestamp_to_date(record.entry_time) == target_date
        )

        exits = sum(
            1
            for record in records
            if record.exit_time
            and _timestamp_to_date(record.exit_time) == target_date
        )

        result.append(
            ChartPoint(
                label=target_date.strftime("%m/%d"),
                value=float(entries),
                secondary=float(exits),
            )
        )

    return result


def _build_weekly(records) -> list[ChartPoint]:
    result = []

    today = datetime.now().date()

    for week in range(3, -1, -1):
        end_date = today.fromordinal(
            today.toordinal() - week * 7
        )
        start_date = end_date.fromordinal(
            end_date.toordinal() - 6
        )

        entries = sum(
            1
            for record in records
            if start_date <= _timestamp_to_date(record.entry_time) <= end_date
        )

        exits = sum(
            1
            for record in records
            if record.exit_time
            and start_date <= _timestamp_to_date(record.exit_time) <= end_date
        )

        result.append(
            ChartPoint(
                label=f"هفته {4 - week}",
                value=float(entries),
                secondary=float(exits),
            )
        )

    return result


def _build_monthly(records) -> list[ChartPoint]:
    result = []

    today = datetime.now()

    for month_offset in range(5, -1, -1):
        month = today.month - month_offset
        year = today.year

        while month <= 0:
            month += 12
            year -= 1

        entries = 0
        exits = 0

        for record in records:
            entry_date = datetime.fromtimestamp(
                record.entry_time / 1000
            )

            if entry_date.year == year and entry_date.month == month:
                entries += 1

            if record.exit_time:
                exit_date = datetime.fromtimestamp(
                    record.exit_time / 1000
                )

                if exit_date.year == year and exit_date.month == month:
                    exits += 1

        result.append(
            ChartPoint(
                label=f"{year}/{month:02d}",
                value=float(entries),
                secondary=float(exits),
            )
        )

    return result


def _build_peak_hours(records) -> list[ChartPoint]:
    counter = Counter()

    for record in records:
        hour = datetime.fromtimestamp(
            record.entry_time / 1000
        ).hour

        counter[hour] += 1

    return [
        ChartPoint(
            label=f"{hour:02d}:00",
            value=float(counter.get(hour, 0)),
        )
        for hour in range(6, 18)
    ]


def _build_top_vehicles(records) -> list[TopVehicle]:
    counter = Counter(
        _plate_key(record.plate)
        for record in records
    )

    result = []

    for plate_text, count in counter.most_common(5):
        parts = plate_text.replace(" - ", " ").split()

        if len(parts) == 4:
            from backend.models import Plate

            plate = Plate(
                two=parts[0],
                letter=parts[1],
                three=parts[2],
                region=parts[3],
            )

            result.append(
                TopVehicle(
                    plate=plate,
                    count=count,
                )
            )

    return result


def _calculate_average_stay(records) -> int:
    durations = []

    for record in records:
        if record.exit_time and record.exit_time > record.entry_time:
            minutes = (
                record.exit_time - record.entry_time
            ) / 60_000

            durations.append(minutes)

    if not durations:
        return 0

    return round(sum(durations) / len(durations))


def _build_by_type(records) -> list[ChartPoint]:
    counter = Counter(
        record.vehicle_type.value
        for record in records
    )

    labels = {
        "CAR": "سواری",
        "PICKUP": "وانت",
        "TRUCK": "کامیون",
        "VAN": "ون / مینی‌بوس",
        "MOTORCYCLE": "موتورسیکلت",
        "OTHER": "سایر",
    }

    return [
        ChartPoint(
            label=labels.get(vehicle_type, vehicle_type),
            value=float(count),
        )
        for vehicle_type, count in counter.items()
    ]