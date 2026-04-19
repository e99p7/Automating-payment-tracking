from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class ProcessPathRequest(BaseModel):
    arenda_path: str = Field(default="data/input/arenda.xlsx")
    bank_path: str = Field(default="data/input/print.xlsx")
    report_path: str = Field(default="data/output/report.xlsx")
    today: Optional[str] = Field(default=None, description="YYYY-MM-DD")
    grace_days: int = 3


class ProcessResponse(BaseModel):
    report_path: str
    summary: dict[str, int]
    preview: list[dict]
