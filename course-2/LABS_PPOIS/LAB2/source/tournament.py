from datetime import date

class Tournament:
    def __init__(self, name: str, date: date, sport_type: str, winner_name: str, prize_amount: float, winner_earnings: float):
        self.name = name
        self.date = date
        self.sport_type = sport_type
        self.winner_name = winner_name
        self.prize_amount = prize_amount
        self.winner_earnings = winner_earnings