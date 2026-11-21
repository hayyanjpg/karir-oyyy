import re
from datetime import datetime
from zoneinfo import ZoneInfo


def now_wib() -> datetime:
    return datetime.now(ZoneInfo("Asia/Jakarta"))


def build_report_filename(full_name: str, extension: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "_", full_name).strip("_") or "User"
    return f"Laporan_Lamaran_{slug}_{now_wib():%Y%m%d}.{extension}"
