# generate_tournaments.py
import random
from xml.dom.minidom import Document
from datetime import datetime, timedelta

sports = ["Tennis", "Football", "Basketball", "Cycling", "Chess", "Swimming", "Athletics"]
tennis_players = ["Djokovic N.", "Alcaraz C.", "Swiatek I.", "Sabalenka A."]
football_teams = ["Argentina", "France", "Brazil", "Manchester City"]


def generate_tournament():
    sport = random.choice(sports)
    date = datetime.now() - timedelta(days=random.randint(0, 365 * 3))

    if sport == "Tennis":
        name = f"{random.choice(['Open', 'Masters', 'Championship'])} {date.year}"
        winner = random.choice(tennis_players)
    elif sport == "Football":
        name = f"{random.choice(['Cup', 'League', 'Tournament'])} {date.year}"
        winner = random.choice(football_teams)
    else:
        name = f"{sport} Competition {date.year}"
        winner = f"Player {random.randint(1, 100)}"

    prize = random.randint(100000, 10000000)
    return {
        "name": name,
        "date": date.strftime("%Y-%m-%d"),
        "sport_type": sport,
        "winner_name": winner,
        "prize_fund": prize
    }


def create_xml(filename, count):
    doc = Document()
    root = doc.createElement("tournaments")
    doc.appendChild(root)

    for _ in range(count):
        t = generate_tournament()
        tour = doc.createElement("tournament")
        for field, value in t.items():
            elem = doc.createElement(field)
            elem.appendChild(doc.createTextNode(str(value)))
            tour.appendChild(elem)
        root.appendChild(tour)

    with open(f"xml-files/{filename}", "w") as f:
        doc.writexml(f, indent="", addindent="  ", newl="\n", encoding="UTF-8")


# Создать 3 файла по 50+ записей
create_xml("tournaments1.xml", 55)
create_xml("tournaments2.xml", 60)
create_xml("tournaments3.xml", 50)