from io import BytesIO

from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from fastapi.responses import StreamingResponse

from memory import load_records


def create_excel_file():
    records = load_records()

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "گزارش تردد"

    headers = [
        "شناسه",
        "پلاک",
        "راننده",
        "نوع خودرو",
        "شرکت",
        "مقصد",
        "زمان ورود",
        "زمان خروج",
        "وضعیت",
        "ثبت‌کننده",
        "توضیحات",
    ]

    sheet.append(headers)

    for cell in sheet[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center")

    for record in records:
        sheet.append([
            record.id,
            f"{record.plate.two} {record.plate.letter} "
            f"{record.plate.three} - {record.plate.region}",
            record.driver,
            record.vehicle_type.value,
            record.company,
            record.destination,
            record.entry_time,
            record.exit_time,
            record.status.value,
            record.registered_by,
            record.description,
        ])

    for column in sheet.columns:
        max_length = 0
        column_letter = column[0].column_letter

        for cell in column:
            if cell.value is not None:
                max_length = max(max_length, len(str(cell.value)))

        sheet.column_dimensions[column_letter].width = min(
            max(max_length + 2, 12),
            30
        )

    output = BytesIO()
    workbook.save(output)
    output.seek(0)

    return output


def export_excel():
    file = create_excel_file()

    return StreamingResponse(
        file,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition": (
                'attachment; filename="traffic_report.xlsx"'
            )
        },
    )