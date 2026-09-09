from datetime import datetime
from xml.dom.minidom import parse, Document
import os
from source.tournament import Tournament


def create_tournament(data, filename="xml_files/tournaments1.xml"):
    # Создаем объект турнира
    tournament = Tournament(
        name=data["name"],
        date=data["date"],
        sport_type=data["sport_type"],
        winner_name=data["winner_name"],
        prize_fund=data["prize_fund"]
    )

    # Добавляем в XML (DOM)
    if os.path.exists(filename):
        dom = parse(filename)
        root = dom.documentElement
    else:
        dom = Document()
        root = dom.createElement("tournaments")
        dom.appendChild(root)

    tour_element = dom.createElement("tournament")

    for field, value in tournament.to_dict().items():
        elem = dom.createElement(field)
        elem.appendChild(dom.createTextNode(str(value)))
        tour_element.appendChild(elem)

    root.appendChild(tour_element)

    with open(filename, "w", encoding="utf-8") as f:
        dom.writexml(f, indent="", addindent="  ", newl="\n", encoding="utf-8")