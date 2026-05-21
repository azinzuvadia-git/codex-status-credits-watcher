from __future__ import annotations

from dataclasses import dataclass


class StatusParseError(RuntimeError):
    pass


@dataclass
class StatusSnapshot:
    five_hour_percent: int
    five_hour_reset: str
    weekly_percent: int
    weekly_reset: str
    credit_balance_text: str
