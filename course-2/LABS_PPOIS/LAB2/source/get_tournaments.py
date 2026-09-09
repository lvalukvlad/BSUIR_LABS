import xml.sax
from typing import List
from source.tournament import Tournament
from datetime import date
from datetime import datetime

class TournamentHandler(xml.sax.ContentHandler):
    def __init__(self):
        self.tournaments: List[Tournament] = []
        self.current_data = ""
        self.current_tag = ""
        self.name = ""
        self.date = None
        self.sport = ""
        self.winner = ""
        self.prize_pool = 0.0
        self.earnings = 0.0

    def startElement(self, tag, attributes):
        self.current_tag = tag

    def endElement(self, tag):
        if tag == "tournament":
            tournament = Tournament(
                name=self.name,
                date=self.date,
                sport_type=self.sport,
                winner_name=self.winner,
                prize_amount=float(self.prize_pool) if self.prize_pool else 0.0,
                winner_earnings=float(self.earnings) if self.earnings else 0.0
            )
            self.tournaments.append(tournament)
            self.name = ""
            self.date = None
            self.sport = ""
            self.winner = ""
            self.prize_pool = 0.0
            self.earnings = 0.0
        elif tag == "name":
            self.name = self.current_data.strip()
        elif tag == "date":
            try:
                self.date = datetime.strptime(self.current_data.strip(), "%Y-%m-%d").date()
            except ValueError:
                self.date = None
        elif tag == "sport":
            self.sport = self.current_data.strip()
        elif tag == "winner":
            self.winner = self.current_data.strip()
        elif tag == "prize_pool":
            self.prize_pool = self.current_data.strip()
        elif tag == "earnings":
            self.earnings = self.current_data.strip()
        self.current_tag = ""
        self.current_data = ""

    def characters(self, content):
        if self.current_tag in ["name", "date", "sport", "winner", "prize_pool", "earnings"]:
            self.current_data += content

def get_tournaments(file_path: str) -> List[Tournament]:
    handler = TournamentHandler()
    parser = xml.sax.make_parser()
    parser.setContentHandler(handler)
    try:
        parser.parse(file_path)
        return handler.tournaments
    except Exception as e:
        print(f"Ошибка при чтении файла {file_path}: {e}")
        return []