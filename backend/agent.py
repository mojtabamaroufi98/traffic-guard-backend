import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from system_prompt import SYSTEM_PROMPT
from tools import (
    get_current_vehicles,
    get_today_records,
    get_traffic_summary,
    search_vehicle,
    get_reports_data,
)


load_dotenv()

API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL")
MODEL = os.getenv("MODEL")


if not API_KEY:
    raise ValueError("API_KEY در فایل .env تنظیم نشده است.")

if not BASE_URL:
    raise ValueError("BASE_URL در فایل .env تنظیم نشده است.")

if not MODEL:
    raise ValueError("MODEL در فایل .env تنظیم نشده است.")


client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL,
)


def _record_to_dict(record):
    return record.model_dump(mode="json")


def build_context(question: str) -> str:
    question_lower = question.lower()

    context = {}

    if any(
        word in question_lower
        for word in [
            "داخل",
            "الان",
            "هم‌اکنون",
            "هم اکنون",
            "مجموعه",
        ]
    ):
        context["current_vehicles"] = [
            _record_to_dict(record)
            for record in get_current_vehicles()
        ]

    if any(
        word in question_lower
        for word in [
            "امروز",
            "ورود",
            "خروج",
            "تردد",
            "آمار",
            "چند",
        ]
    ):
        context["traffic_summary"] = get_traffic_summary()

    if any(
        word in question_lower
        for word in [
            "گزارش",
            "روزانه",
            "هفتگی",
            "ماهانه",
            "پرتردد",
            "اوج",
            "میانگین",
        ]
    ):
        context["reports"] = get_reports_data()

    if any(
        word in question_lower
        for word in [
            "پلاک",
            "سابقه",
            "خودرو",
        ]
    ):
        records = get_today_records()

        context["today_records"] = [
            _record_to_dict(record)
            for record in records
        ]

    if not context:
        context["traffic_summary"] = get_traffic_summary()

    return json.dumps(
        context,
        ensure_ascii=False,
        indent=2,
    )


def ask_agent(question: str) -> str:
    context = build_context(question)

    user_message = f"""
سؤال کاربر:
{question}

اطلاعات واقعی سامانه:
{context}

فقط بر اساس اطلاعات واقعی بالا پاسخ بده.
اگر اطلاعات کافی برای پاسخ وجود ندارد، صریحاً اعلام کن.
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": user_message,
            },
        ],
        temperature=0.1,
    )

    return response.choices[0].message.content or ""