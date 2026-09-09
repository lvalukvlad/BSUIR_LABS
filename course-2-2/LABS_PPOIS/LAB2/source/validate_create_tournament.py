import re
from source.created_tournament import CreatedTournament

def validate_create_tournament(created_tournament: CreatedTournament) -> str:

    name = created_tournament.get_name()
    if not name or not re.match(r"^[\w\s\-]+$", name):
        return "Неверно записано имя турнира"

    date = created_tournament.get_date()
    if not date:
        return "Дата проведения не указана"

    sport_type = created_tournament.get_sport_type()
    if not sport_type or not re.match(r"^[А-ЯЁа-яё\s]+$", sport_type):
        return "Неверно указан тип спорта"

    winner_name = created_tournament.get_winner_name()
    if not winner_name or not re.match(r"^[А-ЯЁ][а-яё]+(?:[-' ]?[А-ЯЁ][а-яё]+)*$", winner_name):
        return "Неверно записано имя победителя"

    prize_amount = created_tournament.get_prize_amount()
    if prize_amount is None or prize_amount <= 0:
        return "Неверно указан размер призовых"

    return ""