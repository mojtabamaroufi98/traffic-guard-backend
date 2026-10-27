import time

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from models import (
    EntryRequest,
    ExitRequest,
    TrafficRecord,
    TrafficStatus,
)
from memory import (
    add_record,
    generate_record_id,
    get_record,
    load_records,
    update_record,
)
from reports import get_report
from excel_export import export_excel
from agent import ask_agent


app = FastAPI(
    title="Traffic Guard API",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "Traffic Guard API is running",
        "status": "ok",
    }


@app.post("/api/auth/login")
def login(data: dict):
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if not username or not password:
        raise HTTPException(
            status_code=400,
            detail="نام کاربری و رمز عبور الزامی است.",
        )

    return {
        "access_token": "demo-token",
        "user": {
            "name": "محمد کریمی",
            "role": "مسئول حراست",
            "employee_id": "EMP-20418",
            "position": "نگهبان شیفت صبح - درب اصلی",
            "phone": "۰۹۱۲۱۲۳۴۵۶۷",
            "email": "m.karimi@company.ir",
        },
    }


@app.get("/api/profile")
def profile():
    return {
        "name": "محمد کریمی",
        "role": "مسئول حراست",
        "employee_id": "EMP-20418",
        "position": "نگهبان شیفت صبح - درب اصلی",
        "phone": "۰۹۱۲۱۲۳۴۵۶۷",
        "email": "m.karimi@company.ir",
    }


@app.get("/api/traffic")
def get_traffic():
    return load_records()


@app.get("/api/traffic/{record_id}")
def get_traffic_record(record_id: str):
    record = get_record(record_id)

    if record is None:
        raise HTTPException(
            status_code=404,
            detail="رکورد مورد نظر پیدا نشد.",
        )

    return record


@app.get("/api/vehicles/inside")
def get_inside_vehicles():
    records = load_records()

    return [
        record
        for record in records
        if record.status == TrafficStatus.INSIDE
    ]


@app.post("/api/traffic/entry")
def register_entry(request: EntryRequest):
    records = load_records()

    plate = request.plate

    duplicate = any(
        record.status == TrafficStatus.INSIDE
        and record.plate.two == plate.two
        and record.plate.letter == plate.letter
        and record.plate.three == plate.three
        and record.plate.region == plate.region
        for record in records
    )

    if duplicate:
        raise HTTPException(
            status_code=400,
            detail="این خودرو در حال حاضر داخل مجموعه است.",
        )

    record = TrafficRecord(
        id=generate_record_id(),
        plate=request.plate,
        driver=request.driver,
        vehicle_type=request.vehicle_type,
        company=request.company,
        destination=request.destination,
        entry_time=int(time.time() * 1000),
        exit_time=None,
        status=TrafficStatus.INSIDE,
        registered_by="محمد کریمی",
        description=request.description,
        image_url=request.image_uri,
    )

    return add_record(record)


@app.post("/api/traffic/exit")
def register_exit(request: ExitRequest):
    record = get_record(request.id)

    if record is None:
        raise HTTPException(
            status_code=404,
            detail="رکورد مورد نظر پیدا نشد.",
        )

    if record.status != TrafficStatus.INSIDE:
        raise HTTPException(
            status_code=400,
            detail="این خودرو قبلاً خارج شده است.",
        )

    updated = record.model_copy(
        update={
            "exit_time": int(time.time() * 1000),
            "status": TrafficStatus.EXITED,
        }
    )

    return update_record(updated)


@app.get("/api/reports")
def reports():
    return get_report()


@app.get("/api/reports/export")
def export_report():
    return export_excel()


@app.post("/api/ai/chat")
def ai_chat(data: dict):
    question = data.get("question", "").strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="سؤال نمی‌تواند خالی باشد.",
        )

    try:
        answer = ask_agent(question)

        return {
            "id": str(int(time.time() * 1000)),
            "from_user": False,
            "text": answer,
            "stats": [],
            "vehicles": [],
            "chart": [],
            "is_error": False,
        }

    except Exception as error:
        return {
            "id": str(int(time.time() * 1000)),
            "from_user": False,
            "text": f"خطا در ارتباط با Agent: {error}",
            "stats": [],
            "vehicles": [],
            "chart": [],
            "is_error": True,
        }