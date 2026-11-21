import re
from datetime import datetime
from zoneinfo import ZoneInfo

WIB = ZoneInfo("Asia/Jakarta")


def now_wib() -> datetime:
    return datetime.now(WIB)


def to_wib_naive(value: datetime | None) -> datetime | None:
    """Convert an aware datetime to naive WIB (Excel rejects tz-aware values)."""
    if value is None:
        return None
    if value.tzinfo is None:
        return value
    return value.astimezone(WIB).replace(tzinfo=None)


def build_report_filename(full_name: str, extension: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "_", full_name).strip("_") or "User"
    return f"Laporan_Lamaran_{slug}_{now_wib():%Y%m%d}.{extension}"
