from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class VehicleType(str, Enum):
    CAR = "CAR"
    PICKUP = "PICKUP"
    TRUCK = "TRUCK"
    VAN = "VAN"
    MOTORCYCLE = "MOTORCYCLE"
    OTHER = "OTHER"


class TrafficStatus(str, Enum):
    INSIDE = "INSIDE"
    EXITED = "EXITED"
    CANCELED = "CANCELED"


class Plate(BaseModel):
    two: str = ""
    letter: str = ""
    three: str = ""
    region: str = ""


class EntryRequest(BaseModel):
    plate: Plate
    driver: str
    vehicle_type: VehicleType
    company: str
    destination: str
    description: str = ""
    image_uri: Optional[str] = None


class ExitRequest(BaseModel):
    id: str


class TrafficRecord(BaseModel):
    id: str
    plate: Plate

    driver: str
    vehicle_type: VehicleType

    company: str
    destination: str

    entry_time: int
    exit_time: Optional[int] = None

    status: TrafficStatus

    registered_by: str = "محمد کریمی"

    description: str = ""
    image_url: Optional[str] = None


class DashboardStats(BaseModel):
    entered: int
    exited: int
    inside: int
    total: int
    entered_trend_percent: Optional[int] = None


class ChartPoint(BaseModel):
    label: str
    value: float
    secondary: Optional[float] = None


class TopVehicle(BaseModel):
    plate: Plate
    count: int


class ReportBundle(BaseModel):
    daily: list[ChartPoint] = Field(default_factory=list)
    weekly: list[ChartPoint] = Field(default_factory=list)
    monthly: list[ChartPoint] = Field(default_factory=list)
    peak_hours: list[ChartPoint] = Field(default_factory=list)
    top_vehicles: list[TopVehicle] = Field(default_factory=list)
    avg_stay_minutes: int = 0
    by_type: list[ChartPoint] = Field(default_factory=list)


class AiStat(BaseModel):
    label: str
    value: str


class AiMessage(BaseModel):
    id: str
    from_user: bool = False
    text: str

    stats: list[AiStat] = Field(default_factory=list)
    vehicles: list[TrafficRecord] = Field(default_factory=list)
    chart: list[ChartPoint] = Field(default_factory=list)

    is_error: bool = False