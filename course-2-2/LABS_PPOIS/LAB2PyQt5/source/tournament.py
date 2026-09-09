from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Tournament:
    name: str
    date: datetime
    sport_type: str
    winner_name: str
    prize_fund: float

    @property
    def winner_earnings(self) -> float:
        return round(self.prize_fund * 0.6, 2)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "date": self.date.strftime("%Y-%m-%d"),
            "sport_type": self.sport_type,
            "winner_name": self.winner_name,
            "prize_fund": self.prize_fund,
            "winner_earnings": self.winner_earnings
        }