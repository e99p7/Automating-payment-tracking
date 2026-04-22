from __future__ import annotations

import calendar
import re
from datetime import date, datetime
from typing import Any

import numpy as np
import pandas as pd


_DATE_RE = re.compile(r"(\d{1,2}[.\-/]\d{1,2}[.\-/]\d{2,4})")


def parse_amount(value: Any) -> float | None:
    if pd.isna(value):
        return None
    if isinstance(value, (int, float, np.integer, np.floating)):
        return float(value)

    s = str(value).strip()
    if not s:
        return None

    s = s.replace("\xa0", " ").replace(" ", "")
    s = re.sub(r"[^\d,\.\-+]", "", s)
    if not s:
        return None

    sign = -1 if s.startswith("-") else 1
    s = s.lstrip("+-")

    if "," in s and "." not in s:
        s = s.replace(",", ".")
    elif "," in s and "." in s:
        if s.rfind(",") > s.rfind("."):
            s = s.replace(".", "").replace(",", ".")
        else:
            s = s.replace(",", "")

    try:
        return sign * float(s)
    except ValueError:
        return None


def normalize_columns(df: pd.DataFrame) -> dict[str, str]:
    return {str(col).lower().strip(): col for col in df.columns}


def find_col_substring(col_map: dict[str, str], substrings: list[str]) -> str | None:
    for key, original in col_map.items():
        for sub in substrings:
            if sub in key:
                return original
    return None


def extract_day(value: Any) -> int | None:
    if pd.isna(value):
        return None
    if isinstance(value, (int, float, np.integer, np.floating)):
        day = int(value)
        return day if 1 <= day <= 31 else None

    dt = pd.to_datetime(value, dayfirst=True, errors="coerce")
    if pd.notna(dt):
        return int(dt.day)

    match = re.search(r"(\d{1,2})", str(value))
    if not match:
        return None
    day = int(match.group(1))
    return day if 1 <= day <= 31 else None


def expected_date_for_day(day: int | None, reference_date: date) -> date | None:
    if day is None:
        return None
    last_day = calendar.monthrange(reference_date.year, reference_date.month)[1]
    return date(reference_date.year, reference_date.month, min(day, last_day))


def extract_date_from_text(value: Any) -> date | None:
    if pd.isna(value):
        return None
    text = str(value)
    match = _DATE_RE.search(text)
    if not match:
        return None
    dt = pd.to_datetime(match.group(1), dayfirst=True, errors="coerce")
    if pd.isna(dt):
        return None
    return dt.date()


def parse_reference_date(value: str | None) -> date:
    if not value:
        return datetime.today().date()
    dt = pd.to_datetime(value, errors="coerce")
    if pd.isna(dt):
        raise ValueError(f"Cannot parse date: {value}")
    return dt.date()


def summarize_statuses(df: pd.DataFrame) -> dict[str, int]:
    if "Статус" not in df.columns or df.empty:
        return {}
    counts = df["Статус"].value_counts(dropna=False).to_dict()
    return {str(k): int(v) for k, v in counts.items()}
