from xml.dom.minidom import parse
import os


def delete_tournaments_from_xml(filename, criteria):
    """Удаляет турниры из XML файла по критериям"""
    if not os.path.exists(filename):
        return 0

    dom = parse(filename)
    root = dom.documentElement
    tournaments = root.getElementsByTagName("tournament")
    deleted_count = 0

    # Идем в обратном порядке для корректного удаления
    for i in range(len(tournaments) - 1, -1, -1):
        tour = tournaments[i]
        matches = True

        for field, value in criteria.items():
            field_node = tour.getElementsByTagName(field)[0]
            field_value = field_node.firstChild.nodeValue

            if field == 'date':
                if field_value != value.strftime("%Y-%m-%d"):
                    matches = False
                    break
            elif field == 'prize_fund':
                if not (value[0] <= float(field_value) <= value[1]):
                    matches = False
                    break
            else:
                if value.lower() not in field_value.lower():
                    matches = False
                    break

        if matches:
            root.removeChild(tour)
            deleted_count += 1

    # Сохраняем изменения
    if deleted_count > 0:
        with open(filename, 'w', encoding='utf-8') as f:
            dom.writexml(f, indent="", addindent="  ", newl="\n", encoding="utf-8")

    return deleted_count