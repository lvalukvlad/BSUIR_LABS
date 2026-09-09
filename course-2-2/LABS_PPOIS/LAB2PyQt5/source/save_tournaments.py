from xml.dom.minidom import Document
from datetime import datetime


def save_tournaments(filename, tournaments):
    doc = Document()
    root = doc.createElement("tournaments")
    doc.appendChild(root)

    for tournament in tournaments:
        tour_element = doc.createElement("tournament")

        for field, value in tournament.to_dict().items():
            elem = doc.createElement(field)
            if isinstance(value, datetime):
                elem.appendChild(doc.createTextNode(value.strftime("%Y-%m-%d")))
            else:
                elem.appendChild(doc.createTextNode(str(value)))
            tour_element.appendChild(elem)

        root.appendChild(tour_element)

    with open(filename, "w", encoding="utf-8") as f:
        doc.writexml(f, indent="", addindent="  ", newl="\n", encoding="utf-8")