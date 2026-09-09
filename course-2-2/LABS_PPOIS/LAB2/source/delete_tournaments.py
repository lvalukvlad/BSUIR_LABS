import xml.sax
import xml.sax.saxutils
import os
from source.tournament import Tournament
from typing import List

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

def delete_tournaments(file_path: str, list_of_tournaments: List[Tournament]):
    try:
        if not os.path.exists(file_path):
            print(f"Ошибка: файл '{file_path}' не найден.")
            return

        handler = TournamentHandler()
        parser = xml.sax.make_parser()
        parser.setContentHandler(handler)
        parser.parse(file_path)

        deleted = False
        updated_tournaments = []

        for tournament in handler.tournaments:
            should_delete = any(
                tournament.get("name") == t.name and
                tournament.get("date") == t.date.isoformat()
                for t in list_of_tournaments
            )
            if not should_delete:
                updated_tournaments.append(tournament)
            else:
                deleted = True

        if deleted:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write('<?xml version="1.0" encoding="utf-8"?>\n')
                f.write("<tournaments>\n")
                for t in updated_tournaments:
                    f.write("  <tournament>\n")
                    for key, value in t.items():
                        tag = xml.sax.saxutils.escape(key)
                        text = xml.sax.saxutils.escape(value)
                        f.write(f"    <{tag}>{text}</{tag}>\n")
                    f.write("  </tournament>\n")
                f.write("</tournaments>\n")
            print("Файл успешно обновлен!")
        else:
            print("Турниры для удаления не найдены.")
    except xml.sax.SAXParseException:
        print(f"Ошибка: некорректный XML-файл '{file_path}'.")