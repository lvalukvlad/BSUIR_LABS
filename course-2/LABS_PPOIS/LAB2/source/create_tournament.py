import xml.sax
import xml.sax.saxutils
import os
from source.tournament import Tournament

class TournamentHandler(xml.sax.ContentHandler):
    def __init__(self):
        self.tournaments = []
        self.current_data = ""
        self.current_tournament = {}

    def startElement(self, tag, attributes):
        self.current_data = tag
        if tag == "tournament":
            self.current_tournament = {}

    def characters(self, content):
        if self.current_data and content.strip():
            self.current_tournament[self.current_data] = content.strip()

    def endElement(self, tag):
        if tag == "tournament" and self.current_tournament:
            self.tournaments.append(self.current_tournament)
        self.current_data = ""

def create_tournament(file_path: str, tournament: Tournament):
    try:
        handler = TournamentHandler()
        parser = xml.sax.make_parser()
        parser.setContentHandler(handler)

        if os.path.exists(file_path):
            parser.parse(file_path)

        new_tournament = {
            "name": tournament.name,
            "date": tournament.date.isoformat(),
            "sport": tournament.sport_type,
            "winner": tournament.winner_name,
            "prize_pool": str(tournament.prize_amount),
            "earnings": str(tournament.winner_earnings)
        }
        handler.tournaments.insert(0, new_tournament)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write('<?xml version="1.0" encoding="utf-8"?>\n')
            f.write("<tournaments>\n")
            for t in handler.tournaments:
                if not t:
                    continue
                f.write("  <tournament>\n")
                for key, value in t.items():
                    tag = xml.sax.saxutils.escape(key)
                    text = xml.sax.saxutils.escape(value)
                    f.write(f"    <{tag}>{text}</{tag}>\n")
                f.write("  </tournament>\n")
            f.write("</tournaments>\n")
    except Exception as e:
        print(f"Ошибка: {e}")