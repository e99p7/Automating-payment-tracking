from __future__ import annotations

import argparse
from pathlib import Path

from src.config import settings
from src.payment_tracker import PaymentTracker
from src.utils import parse_reference_date


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Process payment tracking report from Excel files.")
    parser.add_argument(
        "--arenda",
        default=str(settings.input_dir / settings.default_arenda_file),
        help="Path to arenda.xlsx",
    )
    parser.add_argument(
        "--bank",
        default=str(settings.input_dir / settings.default_bank_file),
        help="Path to print.xlsx",
    )
    parser.add_argument(
        "--report",
        default=str(settings.output_dir / settings.default_report_file),
        help="Where to save output report xlsx.",
    )
    parser.add_argument(
        "--today",
        default=None,
        help="Reference date, e.g. 2026-04-18. Default: today's date.",
    )
    parser.add_argument(
        "--grace-days",
        type=int,
        default=settings.grace_days,
        help="Days after expected payment date before payment becomes overdue.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    today = parse_reference_date(args.today)
    tracker = PaymentTracker(grace_days=args.grace_days)
    result = tracker.process(
        arenda_path=Path(args.arenda),
        bank_path=Path(args.bank),
        report_path=Path(args.report),
        today=today,
    )

    print(f"Report saved to: {result.report_path}")
    print("Summary:", result.summary)
    print(result.report.to_string(index=False))


if __name__ == "__main__":
    main()
