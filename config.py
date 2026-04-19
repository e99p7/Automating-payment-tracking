from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    project_root: Path = Path(__file__).resolve().parents[1]
    input_dir: Path = project_root / "data" / "input"
    output_dir: Path = project_root / "data" / "output"
    default_arenda_file: str = os.getenv("ARENDA_FILE", "arenda.xlsx")
    default_bank_file: str = os.getenv("BANK_FILE", "print.xlsx")
    default_report_file: str = os.getenv("REPORT_FILE", "report.xlsx")
    grace_days: int = int(os.getenv("GRACE_DAYS", "3"))


settings = Settings()
