import xml.sax
from datetime import datetime
from source.tournament import Tournament


class TournamentHandler(xml.sax.ContentHandler):
    def __init__(self):
        self.tournaments = []
        self.current = {}
        self.content = ""

    def startElement(self, name, attrs):
        self.content = ""

    def characters(self, content):
        self.content += content.strip()

    def endElement(self, name):
        if name in ["name", "sport_type", "winner_name"]:
            self.current[name] = self.content
        elif name == "date":
            self.current["date"] = datetime.strptime(self.content, "%Y-%m-%d")
        elif name == "prize_fund":
            self.current["prize_fund"] = float(self.content)
        elif name == "tournament":
            self.tournaments.append(Tournament(**self.current))
            self.current = {}


def load_tournaments(filename):
    handler = TournamentHandler()
    parser = xml.sax.make_parser()
    parser.setContentHandler(handler)
    parser.parse(filename)
    return handler.tournaments