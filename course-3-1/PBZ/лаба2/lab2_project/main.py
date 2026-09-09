import sys

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QTableView, QPushButton,
    QVBoxLayout, QWidget, QFormLayout, QLineEdit, QTextEdit,
    QDateEdit, QComboBox, QMessageBox, QHBoxLayout, QLabel, QDialog,
    QHeaderView, QInputDialog, QGroupBox, QDateEdit, QCheckBox,
    QErrorMessage, QScrollArea, QFrame
)
from PyQt6.QtSql import (
    QSqlDatabase, QSqlQuery, QSqlTableModel, QSqlQueryModel
)
from PyQt6.QtCore import QDate, Qt
from PyQt6.QtGui import QStandardItemModel, QStandardItem # Для QStandardItemModel в отчётах


# === ПАРАМЕТРЫ ПОДКЛЮЧЕНИЯ К БД ===
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'university'  # Убедись, что имя БД правильное
DB_USER = 'postgres'
DB_PASSWORD = '12345'  # Укажи свой пароль, если отличается


# --- КАСТОМНАЯ МОДЕЛЬ ДЛЯ ОТОБРАЖЕНИЯ ДАТ ---
class DateDisplayModel(QSqlQueryModel):
    """
    QSqlQueryModel, который форматирует QDate в строку DD.MM.YYYY для отображения.
    """
    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        # Получаем значение из родительской модели
        value = super().data(index, role)

        # Если роль - DisplayRole (отображение текста в ячейке) и значение - QDate
        if role == Qt.ItemDataRole.DisplayRole and isinstance(value, QDate):
            # Форматируем дату в строку в нужном формате
            # Можно изменить формат, например, на "dd/MM/yyyy" или "yyyy-MM-dd"
            return value.toString("dd.MM.yyyy") if value.isValid() else ""

        # Возвращаем значение как есть для всех остальных случаев
        return value


# --- КЛАССЫ ДИАЛОГОВ ---

class DocumentDialog(QDialog):
    def __init__(self, parent=None, doc_id=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить/Редактировать документ")
        self.doc_id = doc_id
        layout = QFormLayout()

        self.number = QLineEdit()
        self.creation_date = QDateEdit()
        self.creation_date.setDate(QDate.currentDate())
        self.release_date = QDateEdit()
        self.release_date.setDate(QDate.currentDate())
        self.content = QTextEdit()

        # --- ИСПОЛЬЗУЕМ QComboBox с динамической загрузкой типов ---
        self.doc_type_combo = QComboBox()
        self.load_doc_type_combo()

        self.signer_position = QLineEdit()
        self.signer_name = QLineEdit()

        layout.addRow("Номер:", self.number)
        layout.addRow("Дата создания:", self.creation_date)
        layout.addRow("Дата выхода:", self.release_date)
        layout.addRow("Содержание:", self.content)
        layout.addRow("Тип:", self.doc_type_combo) # Используем новый комбобокс
        layout.addRow("Должность подписавшего:", self.signer_position)
        layout.addRow("ФИО подписавшего:", self.signer_name)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(self.save_document)
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)

        layout.addRow(btn_layout)
        self.setLayout(layout)

        if doc_id:
            self.load_document()

    def load_doc_type_combo(self):
        query = QSqlQuery()
        query.exec("SELECT ID, TypeName FROM DocumentType ORDER BY TypeName")
        self.doc_type_combo.clear()
        self.type_id_map = {} # Словарь TypeName -> ID
        while query.next():
            type_id = query.value(0)
            type_name = query.value(1)
            self.doc_type_combo.addItem(type_name, type_id) # Отображаем имя, сохраняем ID как userData
            self.type_id_map[type_name] = type_id

    def load_document(self):
        query = QSqlQuery()
        query.exec(f"SELECT Number, CreationDate, ReleaseDate, Content, DocumentTypeID, SignerPosition, SignerFullName FROM Document WHERE ID = {self.doc_id}")
        if query.next():
            self.number.setText(query.value(0))
            self.creation_date.setDate(query.value(1))
            self.release_date.setDate(query.value(2))
            self.content.setPlainText(query.value(3))
            # self.doc_type.setCurrentText(query.value(4)) # Убираем
            doc_type_id = query.value(4)
            # Найдем индекс в комбобоксе по ID
            index = -1
            for i in range(self.doc_type_combo.count()):
                if self.doc_type_combo.itemData(i) == doc_type_id:
                    index = i
                    break
            if index >= 0:
                self.doc_type_combo.setCurrentIndex(index)
            self.signer_position.setText(query.value(5))
            self.signer_name.setText(query.value(6))

    def save_document(self):
        # --- ИСПОЛЬЗУЕМ РУЧНОЕ ЭКРАНИРОВАНИЕ ---
        def sql_escape(s):
            if s is None:
                return "NULL"
            # Экранируем одинарную кавычку
            escaped = s.replace("'", "''")
            # Заключаем в кавычки для SQL
            return f"'{escaped}'"

        number = self.number.text()
        creation = self.creation_date.date().toString("yyyy-MM-dd")
        release = self.release_date.date().toString("yyyy-MM-dd")
        content = self.content.toPlainText()
        # doc_type = self.doc_type.currentText() # Убираем
        doc_type_id = self.doc_type_combo.currentData() # Получаем ID типа
        signer_pos = self.signer_position.text()
        signer_name = self.signer_name.text()

        query = QSqlQuery()

        # --- НОВОЕ: Проверка на существование номера ---
        check_query = QSqlQuery()
        # Если мы редактируем, исключаем текущий ID из проверки
        where_clause = f"ID != {self.doc_id}" if self.doc_id else "FALSE"
        check_query.exec(f"SELECT COUNT(*) FROM Document WHERE Number = '{number}' AND ({where_clause})")
        if check_query.next() and check_query.value(0) > 0:
            QMessageBox.critical(self, "Ошибка", f"Документ с номером '{number}' уже существует!")
            return # Прерываем выполнение функции, не пытаемся сохранять
        # --- Конец новой проверки ---

        if self.doc_id:
            # --- Обновление через ПРОЦЕДУРУ UpdateDocument ---
            # Используем ручное экранирование
            number_escaped = sql_escape(number)
            creation_escaped = f"'{creation}'"
            release_escaped = f"'{release}'"
            content_escaped = sql_escape(content)
            # doc_type_escaped = sql_escape(doc_type) # Убираем
            doc_type_id_val = doc_type_id # Используем ID напрямую
            signer_pos_escaped = sql_escape(signer_pos)
            signer_name_escaped = sql_escape(signer_name)

            # ВАЖНО: Используем CALL вместо SELECT для процедуры
            sql = f"""CALL UpdateDocument({self.doc_id}, {number_escaped}, {creation_escaped}, {release_escaped}, {content_escaped}, {doc_type_id_val}, {signer_pos_escaped}, {signer_name_escaped})"""
            # print(sql) # Для отладки
            success = query.exec(sql)
        else:
            # --- Создание через функцию CreateDocument ---
            number_escaped = sql_escape(number)
            creation_escaped = f"'{creation}'"
            release_escaped = f"'{release}'"
            content_escaped = sql_escape(content)
            # doc_type_escaped = sql_escape(doc_type) # Убираем
            doc_type_id_val = doc_type_id # Используем ID напрямую
            signer_pos_escaped = sql_escape(signer_pos)
            signer_name_escaped = sql_escape(signer_name)

            sql = f"SELECT CreateDocument({number_escaped}, {creation_escaped}, {release_escaped}, {content_escaped}, {doc_type_id_val}, {signer_pos_escaped}, {signer_name_escaped})"
            # print(sql) # Для отладки
            success = query.exec(sql)

        if success:
            QMessageBox.information(self, "Успех", "Документ сохранён")
            self.accept()
        else:
            QMessageBox.critical(self, "Ошибка", query.lastError().text())


class EventDialog(QDialog):
    def __init__(self, parent=None, event_id=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить/Редактировать мероприятие")
        self.event_id = event_id
        layout = QFormLayout()

        self.name = QLineEdit()
        self.deadline = QDateEdit()
        self.deadline.setDate(QDate.currentDate())
        self.completion_date = QDateEdit()
        self.completion_date.setDate(QDate.fromString("1900-01-01", "yyyy-MM-dd")) # 1900-01-01 как "не установлена"
        self.is_completed = QComboBox()
        self.is_completed.addItems(["Нет", "Да"])

        layout.addRow("Название:", self.name)
        layout.addRow("Дедлайн:", self.deadline)
        layout.addRow("Дата выполнения:", self.completion_date)
        layout.addRow("Выполнено:", self.is_completed)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(self.save_event)
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)

        layout.addRow(btn_layout)
        self.setLayout(layout)

        if event_id:
            self.load_event()

    def load_event(self):
        query = QSqlQuery()
        query.exec(f"SELECT Name, Deadline, CompletionDate, IsCompleted FROM Event WHERE ID = {self.event_id}")
        if query.next():
            self.name.setText(query.value(0))
            self.deadline.setDate(query.value(1))
            if query.value(2): # Если CompletionDate не NULL и не 1900-01-01
                self.completion_date.setDate(query.value(2))
            else:
                # Оставляем 1900-01-01 или устанавливаем на текущую, если нужно
                self.completion_date.setDate(QDate.fromString("1900-01-01", "yyyy-MM-dd"))
            self.is_completed.setCurrentText("Да" if query.value(3) else "Нет")

    def save_event(self):
        # --- ИСПОЛЬЗУЕМ РУЧНОЕ ЭКРАНИРОВАНИЕ ---
        def sql_escape(s):
            if s is None:
                return "NULL"
            # Экранируем одинарную кавычку
            escaped = s.replace("'", "''")
            # Заключаем в кавычки для SQL
            return f"'{escaped}'"

        name = self.name.text()
        deadline = self.deadline.date().toString("yyyy-MM-dd")
        # Проверяем, была ли установлена дата выполнения, и если да, и она не 1900-01-01, то форматируем её
        completion_qdate = self.completion_date.date()
        if completion_qdate.year() != 1900:
            completion = completion_qdate.toString("yyyy-MM-dd")
        else:
            completion = None # Это важно - None для SQL
        is_completed = self.is_completed.currentText() == "Да"

        query = QSqlQuery()
        if self.event_id:
            # --- Обновление через ПРОЦЕДУРУ UpdateEvent ---
            # Используем ручное экранирование
            name_escaped = sql_escape(name)
            deadline_escaped = f"'{deadline}'"
            completion_escaped = sql_escape(completion) # Может быть NULL
            is_completed_str = "TRUE" if is_completed else "FALSE"

            # ВАЖНО: Используем CALL вместо SELECT для процедуры
            sql = f"""CALL UpdateEvent({self.event_id}, {name_escaped}, '{deadline}', {completion_escaped}, {is_completed_str})"""
            # print(sql) # Для отладки
            success = query.exec(sql)
        else:
            # --- Создание через функцию CreateEvent ---
            name_escaped = sql_escape(name)
            deadline_escaped = f"'{deadline}'"
            completion_escaped = sql_escape(completion)
            is_completed_str = "TRUE" if is_completed else "FALSE"

            sql = f"SELECT CreateEvent({name_escaped}, '{deadline}', {completion_escaped}, {is_completed_str})"
            # print(sql) # Для отладки
            success = query.exec(sql)

        if success:
            QMessageBox.information(self, "Успех", "Мероприятие сохранено")
            self.accept()
        else:
            QMessageBox.critical(self, "Ошибка", query.lastError().text())


class CorrespondentDialog(QDialog):
    def __init__(self, parent=None, corr_id=None):
        super().__init__(parent)
        self.setWindowTitle("Корреспондент")
        self.corr_id = corr_id
        layout = QFormLayout()

        self.name = QLineEdit()
        self.position = QLineEdit()

        layout.addRow("ФИО:", self.name)
        layout.addRow("Должность:", self.position)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(self.save_corr)
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)

        layout.addRow(btn_layout)
        self.setLayout(layout)

        if corr_id:
            self.load_corr()

    def load_corr(self):
        query = QSqlQuery()
        query.exec(f"SELECT FullName, Position FROM Correspondent WHERE ID = {self.corr_id}")
        if query.next():
            self.name.setText(query.value(0))
            self.position.setText(query.value(1))

    def save_corr(self):
        name = self.name.text()
        pos = self.position.text()

        query = QSqlQuery()
        if self.corr_id:
            # --- Обновление через UPDATE ---
            # Используем ручное экранирование
            name_escaped = name.replace("'", "''")
            pos_escaped = pos.replace("'", "''")
            sql = f"UPDATE Correspondent SET FullName='{name_escaped}', Position='{pos_escaped}' WHERE ID={self.corr_id}"
            success = query.exec(sql)
        else:
            # --- Создание через функцию CreateCorrespondent ---
            name_escaped = name.replace("'", "''")
            pos_escaped = pos.replace("'", "''")
            sql = f"SELECT CreateCorrespondent('{name_escaped}', '{pos_escaped}')"
            success = query.exec(sql)

        if success:
            QMessageBox.information(self, "Успех", "Корреспондент сохранён")
            self.accept()
        else:
            QMessageBox.critical(self, "Ошибка", query.lastError().text())


class EmployeeDialog(QDialog):
    def __init__(self, parent=None, emp_id=None):
        super().__init__(parent)
        self.setWindowTitle("Сотрудник")
        self.emp_id = emp_id
        layout = QFormLayout()

        self.name = QLineEdit()
        self.position = QLineEdit()

        layout.addRow("ФИО:", self.name)
        layout.addRow("Должность:", self.position)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(self.save_emp)
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)

        layout.addRow(btn_layout)
        self.setLayout(layout)

        if emp_id:
            self.load_emp()

    def load_emp(self):
        query = QSqlQuery()
        query.exec(f"SELECT FullName, Position FROM Employee WHERE ID = {self.emp_id}")
        if query.next():
            self.name.setText(query.value(0))
            self.position.setText(query.value(1))

    def save_emp(self):
        name = self.name.text()
        pos = self.position.text()

        query = QSqlQuery()
        if self.emp_id:
            # --- Обновление через UPDATE ---
            # Используем ручное экранирование
            name_escaped = name.replace("'", "''")
            pos_escaped = pos.replace("'", "''")
            sql = f"UPDATE Employee SET FullName='{name_escaped}', Position='{pos_escaped}' WHERE ID={self.emp_id}"
            success = query.exec(sql)
        else:
            # --- Создание через функцию CreateEmployee ---
            name_escaped = name.replace("'", "''")
            pos_escaped = pos.replace("'", "''")
            sql = f"SELECT CreateEmployee('{name_escaped}', '{pos_escaped}')"
            success = query.exec(sql)

        if success:
            QMessageBox.information(self, "Успех", "Сотрудник сохранён")
            self.accept()
        else:
            QMessageBox.critical(self, "Ошибка", query.lastError().text())


# --- ВКЛАДКИ ---

class DocumentTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        # --- ИСПОЛЬЗУЕМ DateDisplayModel ---
        self.doc_model = DateDisplayModel()
        self.doc_view = QTableView()
        self.doc_view.setModel(self.doc_model)
        self.doc_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Добавить")
        add_btn.clicked.connect(self.add_document)
        edit_btn = QPushButton("Редактировать")
        edit_btn.clicked.connect(self.edit_document)
        del_btn = QPushButton("Удалить")
        del_btn.clicked.connect(self.delete_document)
        refresh_btn = QPushButton("Обновить")
        refresh_btn.clicked.connect(self.load_documents)

        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(del_btn)
        btn_layout.addWidget(refresh_btn)

        layout.addLayout(btn_layout)
        layout.addWidget(self.doc_view)
        self.setLayout(layout)
        self.load_documents()

    def load_documents(self):
        print("Загрузка документов началась...")  # Отладка: видим, что метод вызвался
        query_str = """
        SELECT d.ID, d.Number, d.CreationDate, d.ReleaseDate, d.Content, dt.TypeName, d.SignerPosition, d.SignerFullName
        FROM Document d
        INNER JOIN DocumentType dt ON d.DocumentTypeID = dt.ID
        ORDER BY d.ID
        """
        self.doc_model.setQuery(query_str)

        # Проверяем, есть ли ошибка в запросе
        if self.doc_model.lastError().isValid():
            print("ОШИБКА при загрузке документов:", self.doc_model.lastError().text())
        else:
            print("Запрос выполнен успешно. Количество строк:", self.doc_model.rowCount())
            # --- Устанавливаем заголовки столбцов ---
            self.doc_model.setHeaderData(0, Qt.Orientation.Horizontal, "ID")
            self.doc_model.setHeaderData(1, Qt.Orientation.Horizontal, "Номер")
            self.doc_model.setHeaderData(2, Qt.Orientation.Horizontal, "Дата\nсоздания")
            self.doc_model.setHeaderData(3, Qt.Orientation.Horizontal, "Дата\nвыхода")
            self.doc_model.setHeaderData(4, Qt.Orientation.Horizontal, "Содержание")
            self.doc_model.setHeaderData(5, Qt.Orientation.Horizontal, "Тип")
            self.doc_model.setHeaderData(6, Qt.Orientation.Horizontal, "Подписавший\n(должность)")
            self.doc_model.setHeaderData(7, Qt.Orientation.Horizontal, "Подписавший\n(ФИО)")

    def add_document(self):
        dialog = DocumentDialog(self)
        if dialog.exec():
            self.load_documents() # Вместо self.doc_model.select()

    def edit_document(self):
        index = self.doc_view.currentIndex()
        if not index.isValid():
            return
        doc_id = self.doc_model.data(self.doc_model.index(index.row(), 0)) # ID - первый столбец
        dialog = DocumentDialog(self, doc_id)
        if dialog.exec():
            self.load_documents() # Вместо self.doc_model.select()

    def delete_document(self):
        index = self.doc_view.currentIndex()
        if not index.isValid():
            return
        doc_id = self.doc_model.data(self.doc_model.index(index.row(), 0)) # ID - первый столбец
        reply = QMessageBox.question(self, "Удаление", f"Удалить документ с ID {doc_id}?")
        if reply == QMessageBox.StandardButton.Yes:
            query = QSqlQuery()
            query.exec(f"DELETE FROM Document WHERE ID = {doc_id}")
            # Удаляем также связи
            query.exec(f"DELETE FROM DocumentCorrespondent WHERE DocumentID = {doc_id}")
            query.exec(f"DELETE FROM DocumentEvent WHERE DocumentID = {doc_id}")
            self.load_documents() # Обновляем через load_documents


class EventTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        # --- ИСПОЛЬЗУЕМ DateDisplayModel ---
        self.event_model = DateDisplayModel()
        self.event_view = QTableView()
        self.event_view.setModel(self.event_model)
        self.event_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Добавить мероприятие")
        add_btn.clicked.connect(self.add_event)
        edit_btn = QPushButton("Редактировать")
        edit_btn.clicked.connect(self.edit_event)
        del_btn = QPushButton("Удалить")
        del_btn.clicked.connect(self.delete_event)
        refresh_btn = QPushButton("Обновить")
        refresh_btn.clicked.connect(self.load_events)

        # --- НОВОЕ: Кнопки для управления связями ---
        assign_doc_btn = QPushButton("Привязать к документу")
        assign_doc_btn.clicked.connect(self.assign_event_to_document)
        assign_emp_btn = QPushButton("Назначить исполнителя")
        assign_emp_btn.clicked.connect(self.assign_employee_to_event)

        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(del_btn)
        btn_layout.addWidget(refresh_btn)
        # --- Добавляем новые кнопки ---
        btn_layout.addWidget(assign_doc_btn)
        btn_layout.addWidget(assign_emp_btn)

        layout.addLayout(btn_layout)
        layout.addWidget(self.event_view)
        self.setLayout(layout)
        self.load_events()

    def load_events(self):
        print("Загрузка мероприятий началась...")  # Отладка: видим, что метод вызвался
        query_str = """
        SELECT ID, Name, Deadline, CompletionDate, IsCompleted FROM Event ORDER BY Deadline
        """
        self.event_model.setQuery(query_str)

        # Проверяем, есть ли ошибка в запросе
        if self.event_model.lastError().isValid():
            print("ОШИБКА при загрузке мероприятий:", self.event_model.lastError().text())
        else:
            print("Запрос выполнен успешно. Количество строк:", self.event_model.rowCount())
            # --- Устанавливаем заголовки столбцов ---
            self.event_model.setHeaderData(0, Qt.Orientation.Horizontal, "ID")
            self.event_model.setHeaderData(1, Qt.Orientation.Horizontal, "Название")
            self.event_model.setHeaderData(2, Qt.Orientation.Horizontal, "Дедлайн")
            self.event_model.setHeaderData(3, Qt.Orientation.Horizontal, "Дата выполнения")
            self.event_model.setHeaderData(4, Qt.Orientation.Horizontal, "Выполнено")

    def add_event(self):
        dialog = EventDialog(self)
        if dialog.exec():
            self.load_events() # Вместо self.event_model.select()

    def edit_event(self):
        index = self.event_view.currentIndex()
        if not index.isValid():
            return
        event_id = self.event_model.data(self.event_model.index(index.row(), 0)) # ID - первый столбец
        dialog = EventDialog(self, event_id)
        if dialog.exec():
            self.load_events() # Вместо self.event_model.select()

    def delete_event(self):
        index = self.event_view.currentIndex()
        if not index.isValid():
            return
        event_id = self.event_model.data(self.event_model.index(index.row(), 0)) # ID - первый столбец
        query = QSqlQuery()
        query.exec(f"DELETE FROM Event WHERE ID = {event_id}")
        # Удаляем также связи
        query.exec(f"DELETE FROM DocumentEvent WHERE EventID = {event_id}")
        query.exec(f"DELETE FROM EventAssignment WHERE EventID = {event_id}")
        self.load_events() # Обновляем через load_events

    # --- НОВОЕ: Метод для привязки мероприятия к документу ---
    def assign_event_to_document(self):
        index = self.event_view.currentIndex()
        if not index.isValid():
            QMessageBox.information(self, "Информация", "Выберите мероприятие для привязки.")
            return
        event_id = self.event_model.data(self.event_model.index(index.row(), 0))
        event_name = self.event_model.data(self.event_model.index(index.row(), 1))

        # Диалог для выбора документа
        doc_dialog = AssignDocumentDialog(self, event_id, event_name)
        if doc_dialog.exec():
            self.load_events() # Обновим список мероприятий, возможно, изменились связи

    # --- НОВОЕ: Метод для назначения сотрудника на мероприятие ---
    def assign_employee_to_event(self):
        index = self.event_view.currentIndex()
        if not index.isValid():
            QMessageBox.information(self, "Информация", "Выберите мероприятие для назначения исполнителя.")
            return
        event_id = self.event_model.data(self.event_model.index(index.row(), 0))
        event_name = self.event_model.data(self.event_model.index(index.row(), 1))

        # Диалог для выбора сотрудника
        emp_dialog = AssignEmployeeDialog(self, event_id, event_name)
        if emp_dialog.exec():
            # Назначение уже произошло в диалоге, можно обновить, если нужно что-то отразить
            pass # load_events не обязателен, т.к. это не влияет на отображение в этой таблице напрямую


# --- НОВОЕ: Диалог для привязки мероприятия к документу ---
class AssignDocumentDialog(QDialog):
    def __init__(self, parent=None, event_id=None, event_name=None):
        super().__init__(parent)
        self.setWindowTitle("Привязать мероприятие к документу")
        self.event_id = event_id
        self.event_name = event_name

        layout = QFormLayout()

        layout.addRow(QLabel(f"Мероприятие: {event_name} (ID: {event_id})"))

        self.doc_combo = QComboBox()
        self.load_docs()
        layout.addRow("Выберите документ:", self.doc_combo)

        self.seq_num = QLineEdit()
        self.seq_num.setText("1") # Значение по умолчанию
        layout.addRow("Порядковый номер:", self.seq_num)

        btn_layout = QHBoxLayout()
        assign_btn = QPushButton("Привязать")
        assign_btn.clicked.connect(self.assign)
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(assign_btn)
        btn_layout.addWidget(cancel_btn)

        layout.addRow(btn_layout)
        self.setLayout(layout)

    def load_docs(self):
        query = QSqlQuery()
        # Запрашиваем ID и номер документа для отображения
        query.exec("SELECT ID, Number FROM Document ORDER BY Number")
        while query.next():
            doc_id = query.value(0)
            doc_number = query.value(1)
            # Добавляем номер как отображаемый текст, ID сохраняем как userData
            self.doc_combo.addItem(doc_number, doc_id)

    def assign(self):
        doc_id = self.doc_combo.currentData()
        if doc_id is None:
            QMessageBox.warning(self, "Ошибка", "Выберите документ.")
            return

        seq_num_text = self.seq_num.text()
        try:
            seq_num = int(seq_num_text)
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Порядковый номер должен быть числом.")
            return

        query = QSqlQuery()
        # Вызываем процедуру AddEventToDocument
        # ВНИМАНИЕ: В твоём request.sql AddEventToDocument использует SELECT, а не CALL
        # Если процедура, используйте CALL. Если функция, используйте SELECT.
        # sql = f"SELECT AddEventToDocument({doc_id}, {self.event_id}, {seq_num})"
        # Но AddEventToDocument возвращает VOID, так что лучше использовать CALL и exec.
        sql = f"CALL AddEventToDocument({doc_id}, {self.event_id}, {seq_num})"
        success = query.exec(sql)

        if success:
            QMessageBox.information(self, "Успех", f"Мероприятие '{self.event_name}' привязано к документу.")
            self.accept() # Закрываем диалог при успехе
        else:
            QMessageBox.critical(self, "Ошибка", f"Не удалось привязать мероприятие:\n{query.lastError().text()}")


# --- НОВОЕ: Диалог для назначения сотрудника на мероприятие ---
class AssignEmployeeDialog(QDialog):
    def __init__(self, parent=None, event_id=None, event_name=None):
        super().__init__(parent)
        self.setWindowTitle("Назначить исполнителя мероприятия")
        self.event_id = event_id
        self.event_name = event_name

        layout = QFormLayout()

        layout.addRow(QLabel(f"Мероприятие: {event_name} (ID: {event_id})"))

        self.emp_combo = QComboBox()
        self.load_employees()
        layout.addRow("Выберите сотрудника:", self.emp_combo)

        self.priority = QComboBox()
        self.priority.addItems(["Низкий", "Средний", "Высокий"])
        layout.addRow("Приоритет:", self.priority)

        btn_layout = QHBoxLayout()
        assign_btn = QPushButton("Назначить")
        assign_btn.clicked.connect(self.assign)
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(assign_btn)
        btn_layout.addWidget(cancel_btn)

        layout.addRow(btn_layout)
        self.setLayout(layout)

    def load_employees(self):
        query = QSqlQuery()
        # Запрашиваем ID, ФИО и должность сотрудника для отображения
        query.exec("SELECT ID, FullName, Position FROM Employee ORDER BY FullName")
        while query.next():
            emp_id = query.value(0)
            emp_name = query.value(1)
            emp_pos = query.value(2)
            display_text = f"{emp_name} ({emp_pos})"
            # Добавляем текст как отображаемый, ID сохраняем как userData
            self.emp_combo.addItem(display_text, emp_id)

    def assign(self):
        emp_id = self.emp_combo.currentData()
        if emp_id is None:
            QMessageBox.warning(self, "Ошибка", "Выберите сотрудника.")
            return

        priority = self.priority.currentText()

        query = QSqlQuery()
        # Вызываем процедуру AssignEventToEmployee
        # ВНИМАНИЕ: В твоём request.sql AssignEventToEmployee использует SELECT, а не CALL
        # Предположим, это функция, возвращающая VOID. Лучше использовать CALL.
        # sql = f"SELECT AssignEventToEmployee({self.event_id}, {emp_id}, CURRENT_DATE, '{priority}')"
        # Но AssignEventToEmployee возвращает VOID, так что лучше использовать CALL и exec.
        sql = f"CALL AssignEventToEmployee({self.event_id}, {emp_id}, CURRENT_DATE, '{priority}')"
        success = query.exec(sql)

        if success:
            QMessageBox.information(self, "Успех", f"Сотрудник назначен на мероприятие '{self.event_name}'.")
            self.accept() # Закрываем диалог при успехе
        else:
            QMessageBox.critical(self, "Ошибка", f"Не удалось назначить сотрудника:\n{query.lastError().text()}")


class CorrespondentTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        # --- ИСПОЛЬЗУЕМ DateDisplayModel ---
        self.model = DateDisplayModel()
        self.view = QTableView()
        self.view.setModel(self.model)
        self.view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Добавить")
        add_btn.clicked.connect(self.add_corr)
        edit_btn = QPushButton("Редактировать")
        edit_btn.clicked.connect(self.edit_corr)
        del_btn = QPushButton("Удалить")
        del_btn.clicked.connect(self.delete_corr)
        refresh_btn = QPushButton("Обновить")
        refresh_btn.clicked.connect(self.load_data)

        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(del_btn)
        btn_layout.addWidget(refresh_btn)

        layout.addLayout(btn_layout)
        layout.addWidget(self.view)
        self.setLayout(layout)
        self.load_data()

    def load_data(self):
        print("Загрузка корреспондентов началась...")  # Отладка: видим, что метод вызвался
        query_str = """
        SELECT ID, FullName, Position FROM Correspondent ORDER BY FullName
        """
        self.model.setQuery(query_str)

        # Проверяем, есть ли ошибка в запросе
        if self.model.lastError().isValid():
            print("ОШИБКА при загрузке корреспондентов:", self.model.lastError().text())
        else:
            print("Запрос выполнен успешно. Количество строк:", self.model.rowCount())
            # --- Устанавливаем заголовки столбцов ---
            self.model.setHeaderData(0, Qt.Orientation.Horizontal, "ID")
            self.model.setHeaderData(1, Qt.Orientation.Horizontal, "ФИО")
            self.model.setHeaderData(2, Qt.Orientation.Horizontal, "Должность")

    def add_corr(self):
        dialog = CorrespondentDialog(self)
        if dialog.exec():
            self.load_data()

    def edit_corr(self):
        index = self.view.currentIndex()
        if not index.isValid():
            return
        corr_id = self.model.data(self.model.index(index.row(), 0)) # ID - первый столбец
        dialog = CorrespondentDialog(self, corr_id)
        if dialog.exec():
            self.load_data()

    def delete_corr(self):
        index = self.view.currentIndex()
        if not index.isValid():
            return
        corr_id = self.model.data(self.model.index(index.row(), 0)) # ID - первый столбец
        query = QSqlQuery()
        query.exec(f"DELETE FROM Correspondent WHERE ID = {corr_id}")
        self.load_data()


class EmployeeTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        # --- ИСПОЛЬЗУЕМ DateDisplayModel ---
        self.model = DateDisplayModel()
        self.view = QTableView()
        self.view.setModel(self.model)
        self.view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Добавить")
        add_btn.clicked.connect(self.add_emp)
        edit_btn = QPushButton("Редактировать")
        edit_btn.clicked.connect(self.edit_emp)
        del_btn = QPushButton("Удалить")
        del_btn.clicked.connect(self.delete_emp)
        refresh_btn = QPushButton("Обновить")
        refresh_btn.clicked.connect(self.load_data)

        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(del_btn)
        btn_layout.addWidget(refresh_btn)

        layout.addLayout(btn_layout)
        layout.addWidget(self.view)
        self.setLayout(layout)
        self.load_data()

    def load_data(self):
        print("Загрузка сотрудников началась...")  # Отладка: видим, что метод вызвался
        query_str = """
        SELECT ID, FullName, Position FROM Employee ORDER BY FullName
        """
        self.model.setQuery(query_str)

        # Проверяем, есть ли ошибка в запросе
        if self.model.lastError().isValid():
            print("ОШИБКА при загрузке сотрудников:", self.model.lastError().text())
        else:
            print("Запрос выполнен успешно. Количество строк:", self.model.rowCount())
            # --- Устанавливаем заголовки столбцов ---
            self.model.setHeaderData(0, Qt.Orientation.Horizontal, "ID")
            self.model.setHeaderData(1, Qt.Orientation.Horizontal, "ФИО")
            self.model.setHeaderData(2, Qt.Orientation.Horizontal, "Должность")

    def add_emp(self):
        dialog = EmployeeDialog(self)
        if dialog.exec():
            self.load_data()

    def edit_emp(self):
        index = self.view.currentIndex()
        if not index.isValid():
            return
        emp_id = self.model.data(self.model.index(index.row(), 0)) # ID - первый столбец
        dialog = EmployeeDialog(self, emp_id)
        if dialog.exec():
            self.load_data()

    def delete_emp(self):
        index = self.view.currentIndex()
        if not index.isValid():
            return
        emp_id = self.model.data(self.model.index(index.row(), 0)) # ID - первый столбец
        query = QSqlQuery()
        query.exec(f"DELETE FROM Employee WHERE ID = {emp_id}")
        self.load_data()


# --- НОВАЯ ВКЛАДКА: СПРАВОЧНИКИ ---
class ReferenceTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        # --- Группа: Типы документов ---
        doc_type_group = QGroupBox("Типы документов")
        doc_type_layout = QVBoxLayout()

        self.doc_type_model = DateDisplayModel() # Используем DateDisplayModel
        self.doc_type_view = QTableView()
        self.doc_type_view.setModel(self.doc_type_model)
        self.load_doc_types()

        doc_type_btn_layout = QHBoxLayout()
        add_doc_type_btn = QPushButton("Добавить")
        add_doc_type_btn.clicked.connect(self.add_doc_type)
        edit_doc_type_btn = QPushButton("Редактировать")
        edit_doc_type_btn.clicked.connect(self.edit_doc_type)
        del_doc_type_btn = QPushButton("Удалить")
        del_doc_type_btn.clicked.connect(self.delete_doc_type)
        refresh_doc_type_btn = QPushButton("Обновить")
        refresh_doc_type_btn.clicked.connect(self.load_doc_types)

        doc_type_btn_layout.addWidget(add_doc_type_btn)
        doc_type_btn_layout.addWidget(edit_doc_type_btn)
        doc_type_btn_layout.addWidget(del_doc_type_btn)
        doc_type_btn_layout.addWidget(refresh_doc_type_btn)

        doc_type_layout.addLayout(doc_type_btn_layout)
        doc_type_layout.addWidget(self.doc_type_view)
        doc_type_group.setLayout(doc_type_layout)

        layout.addWidget(doc_type_group)
        self.setLayout(layout)

    def load_doc_types(self):
        print("Загрузка типов документов началась...")  # Отладка
        query_str = """
        SELECT ID, TypeName FROM DocumentType ORDER BY TypeName
        """
        self.doc_type_model.setQuery(query_str)

        # Проверяем, есть ли ошибка в запросе
        if self.doc_type_model.lastError().isValid():
            print("ОШИБКА при загрузке типов документов:", self.doc_type_model.lastError().text())
        else:
            print("Запрос типов документов выполнен успешно. Количество строк:", self.doc_type_model.rowCount())
            # --- Устанавливаем заголовки столбцов ---
            self.doc_type_model.setHeaderData(0, Qt.Orientation.Horizontal, "ID")
            self.doc_type_model.setHeaderData(1, Qt.Orientation.Horizontal, "Название типа")

    def add_doc_type(self):
        text, ok = QInputDialog.getText(self, 'Новый тип документа', 'Введите название типа:')
        if ok and text:
            query = QSqlQuery()
            # Вызываем функцию CreateDocumentType
            query.exec(f"SELECT CreateDocumentType('{text}')") # Используем функцию
            self.load_doc_types()

    def edit_doc_type(self):
        index = self.doc_type_view.currentIndex()
        if not index.isValid():
            QMessageBox.information(self, "Информация", "Выберите тип документа для редактирования.")
            return
        doc_type_id = self.doc_type_model.data(self.doc_type_model.index(index.row(), 0))
        current_name = self.doc_type_model.data(self.doc_type_model.index(index.row(), 1))

        text, ok = QInputDialog.getText(self, 'Редактировать тип документа', 'Введите новое название типа:', text=current_name)
        if ok and text:
            query = QSqlQuery()
            # Вызываем процедуру UpdateDocumentType
            query.exec(f"CALL UpdateDocumentType({doc_type_id}, '{text}')") # Используем CALL
            self.load_doc_types()

    def delete_doc_type(self):
        index = self.doc_type_view.currentIndex()
        if not index.isValid():
            QMessageBox.information(self, "Информация", "Выберите тип документа для удаления.")
            return
        doc_type_id = self.doc_type_model.data(self.doc_type_model.index(index.row(), 0))
        doc_type_name = self.doc_type_model.data(self.doc_type_model.index(index.row(), 1))

        reply = QMessageBox.question(self, "Удаление", f"Удалить тип документа '{doc_type_name}'?")
        if reply == QMessageBox.StandardButton.Yes:
            query = QSqlQuery()
            # Вызываем процедуру DeleteDocumentType
            query.exec(f"CALL DeleteDocumentType({doc_type_id})") # Используем CALL
            self.load_doc_types()


# --- ВКЛАДКА "ОТЧЁТЫ" ---
# ИСПОЛЬЗУЕТ QStandardItemModel и QSqlQuery для выполнения функций
class ReportsTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        # --- ИСПОЛЬЗУЕМ QStandardItemModel для отчётов ---
        self.report_model = QStandardItemModel()
        self.report_view = QTableView()
        self.report_view.setModel(self.report_model)
        self.report_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # --- Группа 1: Невыполненные мероприятия на дату ---
        group1_layout = QHBoxLayout()
        group1_layout.addWidget(QLabel("Невыполненные мероприятия на дату:"))
        self.report_date = QDateEdit()
        self.report_date.setDate(QDate.currentDate())
        group1_layout.addWidget(self.report_date)
        report1_btn = QPushButton("Показать невыполненные мероприятия на дату")
        report1_btn.clicked.connect(self.run_report_1)
        group1_layout.addWidget(report1_btn)

        # --- Группа 2: Мероприятия за период ---
        group2_layout = QHBoxLayout()
        group2_layout.addWidget(QLabel("Мероприятия за период:"))
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addDays(-7))
        group2_layout.addWidget(self.start_date)
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        group2_layout.addWidget(self.end_date)
        report2_btn = QPushButton("Показать мероприятия за период")
        report2_btn.clicked.connect(self.run_report_2)
        group2_layout.addWidget(report2_btn)

        # --- Группа 3: Документы заданного типа ---
        group3_layout = QHBoxLayout()
        group3_layout.addWidget(QLabel("Документы заданного типа:"))
        self.doc_type_combo = QComboBox()
        self.load_doc_type_for_report() # Загружаем типы из БД
        group3_layout.addWidget(self.doc_type_combo)
        report3_btn = QPushButton("Показать документы заданного типа")
        report3_btn.clicked.connect(self.run_report_3)
        group3_layout.addWidget(report3_btn)

        layout.addLayout(group1_layout)
        layout.addLayout(group2_layout)
        layout.addLayout(group3_layout)

        layout.addWidget(self.report_view)
        self.setLayout(layout)

    def load_doc_type_for_report(self):
        query = QSqlQuery()
        query.exec("SELECT TypeName FROM DocumentType ORDER BY TypeName")
        self.doc_type_combo.clear()
        while query.next():
            self.doc_type_combo.addItem(query.value(0))

    def run_report_1(self):
        print("--- Запуск run_report_1 ---") # Отладка
        target_date = self.report_date.date().toString("yyyy-MM-dd")
        print(f"Выбранная дата для отчёта 1: {target_date}") # Отладка: дата
        query_str = f"SELECT * FROM GetUncompletedEventsByDate('{target_date}')"
        print(f"Выполняемый SQL запрос: {query_str}") # Отладка: SQL

        # --- ИСПОЛЬЗУЕМ QSqlQuery и QStandardItemModel ---
        query = QSqlQuery()
        success = query.exec(query_str)

        if success:
            print("Запрос 1 выполнен успешно через QSqlQuery.") # Отладка
            # Очищаем модель перед заполнением
            self.report_model.clear()

            # Получаем количество столбцов
            col_count = query.record().count()
            print(f"Количество столбцов в результате: {col_count}") # Отладка

            # --- Устанавливаем количество столбцов в модели ---
            self.report_model.setColumnCount(col_count)

            # --- Устанавливаем заголовки столбцов для отчёта 1 ---
            headers = [
                "Номер документа",
                "Название мероприятия",
                "Дедлайн",
                "Дата выполнения",
                "Выполнено",
                "ФИО корреспондента",
                "Должность корреспондента",
                "Название подразделения",
                "Дата выхода документа" # Добавлено
            ]
            # Устанавливаем заголовки
            for i in range(min(col_count, len(headers))):
                self.report_model.setHeaderData(i, Qt.Orientation.Horizontal, headers[i])

            # Заполняем модель данными
            while query.next():
                items = []
                for i in range(col_count):
                    val = query.value(i)
                    # --- ФОРМАТИРУЕМ ДАТЫ ВРУЧНУЮ ---
                    if isinstance(val, QDate):
                        formatted_val = val.toString("dd.MM.yyyy")
                    else:
                        formatted_val = str(val) if val is not None else ""
                    item = QStandardItem(formatted_val)
                    items.append(item)
                self.report_model.appendRow(items)

            print(f"Данные загружены в модель. Количество строк: {self.report_model.rowCount()}") # Отладка
        else:
            error_msg = query.lastError().text()
            print(f"ОШИБКА при выполнении запроса 1 через QSqlQuery: {error_msg}") # Отладка: ошибка
            QMessageBox.critical(self, "Ошибка отчёта", f"Не удалось выполнить отчёт 1:\n{error_msg}")

    def run_report_2(self):
        print("--- Запуск run_report_2 ---") # Отладка
        start = self.start_date.date().toString("yyyy-MM-dd")
        end = self.end_date.date().toString("yyyy-MM-dd")
        print(f"Выбранный период для отчёта 2: {start} - {end}") # Отладка: период
        query_str = f"SELECT * FROM GetEventsByPeriod('{start}', '{end}')"
        print(f"Выполняемый SQL запрос: {query_str}") # Отладка: SQL

        # --- ИСПОЛЬЗУЕМ QSqlQuery и QStandardItemModel ---
        query = QSqlQuery()
        success = query.exec(query_str)

        if success:
            print("Запрос 2 выполнен успешно через QSqlQuery.") # Отладка
            # Очищаем модель перед заполнением
            self.report_model.clear()

            # Получаем количество столбцов
            col_count = query.record().count()
            print(f"Количество столбцов в результате: {col_count}") # Отладка

            # --- Устанавливаем количество столбцов в модели ---
            self.report_model.setColumnCount(col_count)

            # --- Устанавливаем заголовки столбцов для отчёта 2 ---
            headers = [
                "Название мероприятия",
                "Дедлайн",
                "Дата выполнения",
                "Выполнено",
                "Номер документа",
                "Тип документа" # Было DocumentType, стало DocumentTypeName
            ]
            # Устанавливаем заголовки
            for i in range(min(col_count, len(headers))):
                self.report_model.setHeaderData(i, Qt.Orientation.Horizontal, headers[i])

            # Заполняем модель данными
            while query.next():
                items = []
                for i in range(col_count):
                    val = query.value(i)
                    # --- ФОРМАТИРУЕМ ДАТЫ ВРУЧНУЮ ---
                    if isinstance(val, QDate):
                        formatted_val = val.toString("dd.MM.yyyy")
                    else:
                        formatted_val = str(val) if val is not None else ""
                    item = QStandardItem(formatted_val)
                    items.append(item)
                self.report_model.appendRow(items)

            print(f"Данные загружены в модель. Количество строк: {self.report_model.rowCount()}") # Отладка
        else:
            error_msg = query.lastError().text()
            print(f"ОШИБКА при выполнении запроса 2 через QSqlQuery: {error_msg}") # Отладка: ошибка
            QMessageBox.critical(self, "Ошибка отчёта", f"Не удалось выполнить отчёт 2:\n{error_msg}")

    def run_report_3(self):
        print("--- Запуск run_report_3 ---") # Отладка
        doc_type_name = self.doc_type_combo.currentText()
        print(f"Выбранный тип документа для отчёта 3: {doc_type_name}") # Отладка: тип
        query_str = f"SELECT * FROM GetDocumentsByTypeCurrentDate('{doc_type_name}')"
        print(f"Выполняемый SQL запрос: {query_str}") # Отладка: SQL

        # --- ИСПОЛЬЗУЕМ QSqlQuery и QStandardItemModel ---
        query = QSqlQuery()
        success = query.exec(query_str)

        if success:
            print("Запрос 3 выполнен успешно через QSqlQuery.") # Отладка
            # Очищаем модель перед заполнением
            self.report_model.clear()

            # Получаем количество столбцов
            col_count = query.record().count()
            print(f"Количество столбцов в результате: {col_count}") # Отладка

            # --- Устанавливаем количество столбцов в модели ---
            self.report_model.setColumnCount(col_count)

            # --- Устанавливаем заголовки столбцов для отчёта 3 ---
            headers = [
                "Название предприятия",
                "Текущая дата",
                "Тип документа", # Было DocumentType, стало DocumentTypeName
                "Номер документа",
                "Дата документа",
                "Пометка о выполнении"
            ]
            # Устанавливаем заголовки
            for i in range(min(col_count, len(headers))):
                self.report_model.setHeaderData(i, Qt.Orientation.Horizontal, headers[i])

            # Заполняем модель данными
            while query.next():
                items = []
                for i in range(col_count):
                    val = query.value(i)
                    # --- ФОРМАТИРУЕМ ДАТЫ ВРУЧНУЮ ---
                    if isinstance(val, QDate):
                        formatted_val = val.toString("dd.MM.yyyy")
                    else:
                        formatted_val = str(val) if val is not None else ""
                    item = QStandardItem(formatted_val)
                    items.append(item)
                self.report_model.appendRow(items)

            print(f"Данные загружены в модель. Количество строк: {self.report_model.rowCount()}") # Отладка
        else:
            error_msg = query.lastError().text()
            print(f"ОШИБКА при выполнении запроса 3 через QSqlQuery: {error_msg}") # Отладка: ошибка
            QMessageBox.critical(self, "Ошибка отчёта", f"Не удалось выполнить отчёт 3:\n{error_msg}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Учёт приказов и распоряжений")
        self.resize(1200, 800)

        # Подключение к БД
        db = QSqlDatabase.addDatabase("QPSQL")
        db.setHostName(DB_HOST)
        db.setDatabaseName(DB_NAME)
        db.setUserName(DB_USER)
        db.setPassword(DB_PASSWORD)
        db.setPort(int(DB_PORT))
        if not db.open():
            QMessageBox.critical(None, "Ошибка", "Не удалось подключиться к БД!")
            sys.exit(1)

        tabs = QTabWidget()

        # Вкладка "Документы"
        doc_tab = DocumentTab()
        tabs.addTab(doc_tab, "Документы")

        # Вкладка "Мероприятия"
        event_tab = EventTab()
        tabs.addTab(event_tab, "Мероприятия")

        # Вкладка "Корреспонденты"
        corr_tab = CorrespondentTab()
        tabs.addTab(corr_tab, "Корреспонденты")

        # Вкладка "Сотрудники"
        emp_tab = EmployeeTab()
        tabs.addTab(emp_tab, "Сотрудники")

        # Вкладка "Отчёты"
        report_tab = ReportsTab()
        tabs.addTab(report_tab, "Отчёты")

        # --- НОВАЯ ВКЛАДКА: СПРАВОЧНИКИ ---
        ref_tab = ReferenceTab()
        tabs.addTab(ref_tab, "Справочники")

        self.setCentralWidget(tabs)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())