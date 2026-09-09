from datetime import date
from source.tournament import Tournament

class CreatedTournament:
    __name: str | None = None
    __date: date | None = None
    __sport_type: str | None = None
    __winner_name: str | None = None
    __prize_amount: float | None = None

    def get_tournament(self) -> Tournament | None:
        if not all([self.__name, self.__date, self.__sport_type, self.__winner_name, self.__prize_amount is not None]):
            return None
        return Tournament(
            name=self.__name,
            date=self.__date,
            sport_type=self.__sport_type,
            winner_name=self.__winner_name,
            prize_amount=self.__prize_amount,
            winner_earnings=round(self.__prize_amount * 0.6, 2)
        )

    def set_name(self, name: str):
        self.__name = name.strip() if name else None
        print(f"Set name: {self.__name}")

    def get_name(self) -> str | None:
        return self.__name

    def set_date(self, event_date: date):
        self.__date = event_date
        print(f"Set date: {self.__date}")  # Отладка

    def get_date(self) -> date | None:
        return self.__date

    def set_sport_type(self, sport_type: str):
        self.__sport_type = sport_type.strip() if sport_type else None
        print(f"Set sport type: {self.__sport_type}")  # Отладка

    def get_sport_type(self) -> str | None:
        return self.__sport_type

    def set_winner_name(self, winner_name: str):
        self.__winner_name = winner_name.strip() if winner_name else None
        print(f"Set winner name: {self.__winner_name}")  # Отладка

    def get_winner_name(self) -> str | None:
        return self.__winner_name

    def set_prize_amount(self, amount: float):
        self.__prize_amount = amount if amount is not None and amount >= 0 else None
        print(f"Set prize amount: {self.__prize_amount}")  # Отладка

    def get_prize_amount(self) -> float | None:
        return self.__prize_amount