from typing import List, Optional
from source.tournament import Tournament
from datetime import date, datetime

class HighlightedTournaments:
    __tournaments: Optional[List[Tournament]] = None

    __name: Optional[str] = None
    __date: Optional[date] = None
    __sport_type: Optional[str] = None
    __winner_name: Optional[str] = None
    __min_prize_amount: Optional[float] = None
    __max_prize_amount: Optional[float] = None
    __min_winner_earnings: Optional[float] = None
    __max_winner_earnings: Optional[float] = None

    def __init__(self, tournaments: Optional[List[Tournament]] = None):
        self.__tournaments = tournaments

    @property
    def tournaments(self):
        return self.__tournaments

    @tournaments.setter
    def tournaments(self, tournaments: List[Tournament]):
        self.__tournaments = tournaments

    def get_tournaments(self) -> Optional[List[Tournament]]:
        if self.__tournaments is None:
            return None

        filtered: List[Tournament] = []

        for t in self.__tournaments:
            if self.__name and self.__name not in t.name:
                continue

            if self.__date and t.date != self.__date:
                continue

            if self.__sport_type and self.__sport_type not in t.sport_type:
                continue

            if self.__winner_name and self.__winner_name not in t.winner_name:
                continue

            if self.__min_prize_amount is not None and t.prize_amount < self.__min_prize_amount:
                continue

            if self.__max_prize_amount is not None and t.prize_amount > self.__max_prize_amount:
                continue

            if self.__min_winner_earnings is not None and t.winner_earnings < self.__min_winner_earnings:
                continue

            if self.__max_winner_earnings is not None and t.winner_earnings > self.__max_winner_earnings:
                continue

            filtered.append(t)

        return filtered if filtered else None

    def set_name(self, name: Optional[str]):
        self.__name = name.strip() if name else None

    def get_name(self) -> Optional[str]:
        return self.__name

    def set_date(self, date: Optional[date]):
        self.__date = date

    def get_date(self) -> Optional[date]:
        return self.__date

    def set_sport_type(self, sport_type: Optional[str]):
        self.__sport_type = sport_type.strip() if sport_type else None

    def get_sport_type(self) -> Optional[str]:
        return self.__sport_type

    def set_winner_name(self, winner_name: Optional[str]):
        self.__winner_name = winner_name.strip() if winner_name else None

    def get_winner_name(self) -> Optional[str]:
        return self.__winner_name

    def set_min_prize_amount(self, min_prize: Optional[float]):
        self.__min_prize_amount = min_prize

    def get_min_prize_amount(self) -> Optional[float]:
        return self.__min_prize_amount

    def set_max_prize_amount(self, max_prize: Optional[float]):
        self.__max_prize_amount = max_prize

    def get_max_prize_amount(self) -> Optional[float]:
        return self.__max_prize_amount

    def set_min_winner_earnings(self, min_earnings: Optional[float]):
        self.__min_winner_earnings = min_earnings

    def get_min_winner_earnings(self) -> Optional[float]:
        return self.__min_winner_earnings

    def set_max_winner_earnings(self, max_earnings: Optional[float]):
        self.__max_winner_earnings = max_earnings

    def get_max_winner_earnings(self) -> Optional[float]:
        return self.__max_winner_earnings

    def get_min_date(self) -> date:
        if not self.__tournaments or not any(t.date for t in self.__tournaments):
            return date.min
        return min(t.date for t in self.__tournaments if t.date)

    def get_max_date(self) -> date:
        if not self.__tournaments or not any(t.date for t in self.__tournaments):
            return date.min
        return max(t.date for t in self.__tournaments if t.date)