from PyQt5.QtWidgets import QFileDialog
import os


def init_data_dir():
    """Инициализирует папки и создает примеры данных"""
    if not os.path.exists("xml_files"):
        os.makedirs("xml_files")

    # Создаем пример файла если нет ни одного
    if not os.listdir("xml_files"):
        from xml.dom.minidom import Document
        doc = Document()
        root = doc.createElement("tournaments")
        doc.appendChild(root)

        with open("xml_files/tournaments1.xml", "w") as f:
            doc.writexml(f, indent="", addindent="  ", newl="\n", encoding="utf-8")


def get_open_filename(parent):
    filename, _ = QFileDialog.getOpenFileName(
        parent,
        "Открыть файл турниров",
        "xml_files",
        "XML Files (*.xml)"
    )
    return filename