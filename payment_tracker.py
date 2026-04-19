from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

from .excel_io import read_bank_statement, read_first_sheet, write_report
from .utils import (
    expected_date_for_day,
    extract_day,
    find_col_substring,
    normalize_columns,
    parse_amount,
    summarize_statuses,
)


@dataclass
class TrackingResult:
    report: pd.DataFrame
    report_path: Path
    summary: dict[str, int]


class PaymentTracker:
    def __init__(self, grace_days: int = 3) -> None:
        self.grace_days = grace_days

    @staticmethod
    def _find_best_amount_col(arenda: pd.DataFrame, col_map: dict[str, str]) -> str | None:
        preferred = ["сумма", "amount", "стоимость"]
        for pref in preferred:
            for key, original in col_map.items():
                if pref in key:
                    return original
        return None

    @staticmethod
    def _find_best_date_col(arenda: pd.DataFrame, col_map: dict[str, str]) -> str | None:
        preferred = ["дата", "срок", "ожидаем", "date"]
        for pref in preferred:
            for key, original in col_map.items():
                if pref in key:
                    return original
        return None

    def _prepare_arenda(self, arenda: pd.DataFrame, today: date) -> pd.DataFrame:
        col_map = normalize_columns(arenda)
        garage_col = find_col_substring(col_map, ["гараж", "наимен", "назван", "garage"])
        date_col = self._find_best_date_col(arenda, col_map)
        amount_col = self._find_best_amount_col(arenda, col_map)
        tenant_col = find_col_substring(col_map, ["аренд", "имя", "фамил", "tenant"])

        if not garage_col or not amount_col or not date_col:
            raise ValueError(
                "Не найдены нужные колонки в arenda.xlsx. "
                "Нужны колонки для гаража, даты оплаты и суммы."
            )

        selected = [garage_col, date_col, amount_col] + ([tenant_col] if tenant_col else [])
        ar = arenda[selected].copy()
        ar.columns = ["garage", "expected_date_raw", "amount"] + (["tenant"] if tenant_col else [])
        ar["garage"] = ar["garage"].astype(str)
        ar["amount_parsed"] = ar["amount"].apply(parse_amount)
        ar["expected_day"] = ar["expected_date_raw"].apply(extract_day)
        ar["expected_date"] = ar["expected_day"].apply(lambda d: expected_date_for_day(d, today))
        return ar

    def _prepare_bank(self, bank: pd.DataFrame) -> pd.DataFrame:
        bank_norm = bank.copy()

        # If it is already extracted from Sber PDF-like table, just keep canonical columns.
        if {"amount_parsed", "date_parsed"}.issubset(bank_norm.columns):
            return bank_norm

        col_map = normalize_columns(bank_norm)
        amount_col = find_col_substring(col_map, ["сумма", "amount", "кредит", "зачисл", "credit"])
        date_col = find_col_substring(col_map, ["дата операции", "дата", "date", "операц", "платеж", "posted"])

        if not amount_col or not date_col:
            raise ValueError("Не удалось разобрать print.xlsx: не найдены сумма и дата.")

        bank_norm = bank_norm[[amount_col, date_col]].copy()
        bank_norm.columns = ["amount_raw", "date_raw"]
        bank_norm["amount_parsed"] = bank_norm["amount_raw"].apply(parse_amount)
        bank_norm["date_parsed"] = pd.to_datetime(
            bank_norm["date_raw"], dayfirst=True, errors="coerce"
        ).dt.date
        bank_norm = bank_norm[bank_norm["amount_parsed"].notna() & bank_norm["date_parsed"].notna()].copy()
        return bank_norm

    def process(
        self,
        arenda_path: str | Path,
        bank_path: str | Path,
        report_path: str | Path,
        today: date,
    ) -> TrackingResult:
        arenda = read_first_sheet(arenda_path)
        bank = read_bank_statement(bank_path)

        ar = self._prepare_arenda(arenda, today)
        bank_norm = self._prepare_bank(bank)

        results: list[dict] = []
        used_bank_rows: set[int] = set()

        for _, row in ar.iterrows():
            garage = row["garage"]
            expected_date = row["expected_date"]
            amount = row["amount_parsed"]

            payment_date = None
            matched_amount = None

            if amount is not None:
                tolerance = 1e-2
                candidates = bank_norm[
                    bank_norm["amount_parsed"].notna()
                    & (bank_norm["amount_parsed"].sub(amount).abs() <= tolerance)
                ].copy()

                if "row_number" in candidates.columns and used_bank_rows:
                    candidates = candidates[~candidates["row_number"].isin(used_bank_rows)]

                if expected_date is not None and "date_parsed" in candidates.columns:
                    # Prefer payments in the same month and not earlier than the expected date.
                    preferred = candidates[candidates["date_parsed"] >= expected_date]
                    if not preferred.empty:
                        candidates = preferred

                if not candidates.empty:
                    candidates = candidates.sort_values("date_parsed", na_position="last")
                    match = candidates.iloc[0]
                    payment_date = match.get("date_parsed")
                    matched_amount = match.get("amount_parsed")
                    if "row_number" in match.index:
                        used_bank_rows.add(int(match["row_number"]))

            if payment_date is not None:
                status = "получен"
            else:
                if expected_date and today > (expected_date + timedelta(days=self.grace_days)):
                    status = "просрочен"
                else:
                    status = "срок не наступил"

            results.append(
                {
                    "Название гаража": garage,
                    "Ожидаемая дата оплаты": expected_date,
                    "Сумма оплаты": amount,
                    "Статус": status,
                    "Дата платежа (из выписки)": payment_date,
                    "Совпавшая сумма": matched_amount,
                }
            )

        report = pd.DataFrame(results)
        out_path = write_report(report, report_path)
        return TrackingResult(report=report, report_path=out_path, summary=summarize_statuses(report))
