-- Вставка тестовых данных (если таблицы пусты)
DO $$
BEGIN
    IF (SELECT COUNT(*) FROM Company) = 0 THEN
        INSERT INTO Company (Name, LegalAddress) VALUES ('ООО "Рога и Копыта"', 'г. Минск, ул. Тестовая, д. 1');
    END IF;

    IF (SELECT COUNT(*) FROM Department) = 0 THEN
        INSERT INTO Department (Name, HierarchyLevel, ParentDepartmentID) VALUES
        ('Администрация', 1, NULL),
        ('Отдел разработки', 2, (SELECT ID FROM Department WHERE Name = 'Администрация')),
        ('Отдел кадров', 2, (SELECT ID FROM Department WHERE Name = 'Администрация')),
        ('Отдел охраны труда', 2, (SELECT ID FROM Department WHERE Name = 'Администрация'));
    END IF;

    IF (SELECT COUNT(*) FROM Correspondent) = 0 THEN
        INSERT INTO Correspondent (FullName, Position) VALUES
        ('Петров П.П.', 'Генеральный директор'),
        ('Иванов И.И.', 'Главный инженер'),
        ('Сидоров С.С.', 'Начальник отдела разработки'),
        ('Козлова К.К.', 'Начальник отдела кадров');
    END IF;

    IF (SELECT COUNT(*) FROM Employee) = 0 THEN
        INSERT INTO Employee (FullName, Position) VALUES
        ('Михайлов М.М.', 'Ведущий инженер'),
        ('Федоров Ф.Ф.', 'Специалист'),
        ('Алексеев А.А.', 'Главный специалист'),
        ('Егорова Е.Е.', 'Инженер');
    END IF;

    IF (SELECT COUNT(*) FROM Document) = 0 THEN
        INSERT INTO Document (Number, CreationDate, ReleaseDate, Content, DocumentTypeID, SignerPosition, SignerFullName) VALUES
        ('П-2025-001', '2025-12-01', '2025-12-02', 'Утвердить план мероприятий по повышению пожарной безопасности на 2025 год.', (SELECT ID FROM DocumentType WHERE TypeName = 'Приказ'), 'Генеральный директор', 'Петров П.П.'),
        ('Р-2025-001', '2025-12-05', '2025-12-05', 'Назначить ответственных за проверку пожарного оборудования.', (SELECT ID FROM DocumentType WHERE TypeName = 'Распоряжение'), 'Главный инженер', 'Иванов И.И.'),
        ('У-2025-001', '2025-12-10', '2025-12-10', 'О введении в действие нового регламента.', (SELECT ID FROM DocumentType WHERE TypeName = 'Указание'), 'Начальник отдела разработки', 'Сидоров С.С.');
    END IF;

    IF (SELECT COUNT(*) FROM Event) = 0 THEN
        INSERT INTO Event (Name, Deadline, CompletionDate, IsCompleted) VALUES
        ('Проверить пожарные извещатели в корпусе А', '2025-12-15', '2025-12-14', TRUE), -- Выполнено
        ('Провести инструктаж по пожарной безопасности', '2025-12-18', NULL, FALSE), -- Не выполнено, просрочено (17.12.2025)
        ('Подготовить отчет по проверке охраны труда', '2025-12-20', NULL, FALSE), -- Не выполнено, дедлайн в будущем
        ('Обновить инструкции по охране труда', '2025-12-10', '2025-12-10', TRUE), -- Выполнено
        ('Назначить ответственных за оборудование', '2025-12-06', '2025-12-06', TRUE), -- Выполнено
        ('Ознакомить персонал с новым регламентом', '2025-12-11', NULL, FALSE); -- Не выполнено, просрочено (17.12.2025)
    END IF;

    -- Связи
    IF (SELECT COUNT(*) FROM DocumentEvent) = 0 THEN
        INSERT INTO DocumentEvent (DocumentID, EventID, SequenceNumber) VALUES
        ((SELECT ID FROM Document WHERE Number = 'П-2025-001'), (SELECT ID FROM Event WHERE Name = 'Проверить пожарные извещатели в корпусе А'), 1),
        ((SELECT ID FROM Document WHERE Number = 'П-2025-001'), (SELECT ID FROM Event WHERE Name = 'Провести инструктаж по пожарной безопасности'), 2),
        ((SELECT ID FROM Document WHERE Number = 'П-2025-001'), (SELECT ID FROM Event WHERE Name = 'Подготовить отчет по проверке охраны труда'), 3),
        ((SELECT ID FROM Document WHERE Number = 'Р-2025-001'), (SELECT ID FROM Event WHERE Name = 'Назначить ответственных за оборудование'), 1),
        ((SELECT ID FROM Document WHERE Number = 'У-2025-001'), (SELECT ID FROM Event WHERE Name = 'Ознакомить персонал с новым регламентом'), 1);
    END IF;

    IF (SELECT COUNT(*) FROM DocumentCorrespondent) = 0 THEN
        INSERT INTO DocumentCorrespondent (CorrespondentID, DocumentID, AuthorAssignmentDate) VALUES
        ((SELECT ID FROM Correspondent WHERE FullName = 'Петров П.П.'), (SELECT ID FROM Document WHERE Number = 'П-2025-001'), '2025-12-01'),
        ((SELECT ID FROM Correspondent WHERE FullName = 'Иванов И.И.'), (SELECT ID FROM Document WHERE Number = 'Р-2025-001'), '2025-12-05'),
        ((SELECT ID FROM Correspondent WHERE FullName = 'Сидоров С.С.'), (SELECT ID FROM Document WHERE Number = 'У-2025-001'), '2025-12-10');
    END IF;

    IF (SELECT COUNT(*) FROM EventAssignment) = 0 THEN
        INSERT INTO EventAssignment (EventID, EmployeeID, AssignmentDate, Priority) VALUES
        ((SELECT ID FROM Event WHERE Name = 'Проверить пожарные извещатели в корпусе А'), (SELECT ID FROM Employee WHERE FullName = 'Михайлов М.М.'), '2025-12-01', 'Высокий'),
        ((SELECT ID FROM Event WHERE Name = 'Провести инструктаж по пожарной безопасности'), (SELECT ID FROM Employee WHERE FullName = 'Федоров Ф.Ф.'), '2025-12-05', 'Средний'),
        ((SELECT ID FROM Event WHERE Name = 'Подготовить отчет по проверке охраны труда'), (SELECT ID FROM Employee WHERE FullName = 'Алексеев А.А.'), '2025-12-05', 'Низкий'),
        ((SELECT ID FROM Event WHERE Name = 'Назначить ответственных за оборудование'), (SELECT ID FROM Employee WHERE FullName = 'Егорова Е.Е.'), '2025-12-05', 'Высокий'),
        ((SELECT ID FROM Event WHERE Name = 'Ознакомить персонал с новым регламентом'), (SELECT ID FROM Employee WHERE FullName = 'Михайлов М.М.'), '2025-12-10', 'Средний');
    END IF;

    IF (SELECT COUNT(*) FROM EmployeeDepartment) = 0 THEN
        INSERT INTO EmployeeDepartment (EmployeeID, DepartmentID, StartDate, Status) VALUES
        ((SELECT ID FROM Employee WHERE FullName = 'Михайлов М.М.'), (SELECT ID FROM Department WHERE Name = 'Отдел разработки'), '2021-01-01', 'Активен'),
        ((SELECT ID FROM Employee WHERE FullName = 'Федоров Ф.Ф.'), (SELECT ID FROM Department WHERE Name = 'Отдел разработки'), '2021-01-01', 'Активен'),
        ((SELECT ID FROM Employee WHERE FullName = 'Алексеев А.А.'), (SELECT ID FROM Department WHERE Name = 'Отдел кадров'), '2021-01-01', 'Активен'),
        ((SELECT ID FROM Employee WHERE FullName = 'Егорова Е.Е.'), (SELECT ID FROM Department WHERE Name = 'Отдел охраны труда'), '2021-01-01', 'Активен');
    END IF;

    IF (SELECT COUNT(*) FROM CorrespondentDepartment) = 0 THEN
        INSERT INTO CorrespondentDepartment (CorrespondentID, DepartmentID, StartDate, Status) VALUES
        ((SELECT ID FROM Correspondent WHERE FullName = 'Петров П.П.'), (SELECT ID FROM Department WHERE Name = 'Администрация'), '2020-01-01', 'Активен'),
        ((SELECT ID FROM Correspondent WHERE FullName = 'Иванов И.И.'), (SELECT ID FROM Department WHERE Name = 'Отдел разработки'), '2020-01-01', 'Активен'),
        ((SELECT ID FROM Correspondent WHERE FullName = 'Сидоров С.С.'), (SELECT ID FROM Department WHERE Name = 'Отдел разработки'), '2020-01-01', 'Активен'),
        ((SELECT ID FROM Correspondent WHERE FullName = 'Козлова К.К.'), (SELECT ID FROM Department WHERE Name = 'Отдел кадров'), '2020-01-01', 'Активен');
    END IF;

    IF (SELECT COUNT(*) FROM DepartmentCompany) = 0 THEN
        INSERT INTO DepartmentCompany (DepartmentID, CompanyID, InclusionDate) VALUES
        ((SELECT ID FROM Department WHERE Name = 'Администрация'), (SELECT ID FROM Company WHERE Name = 'ООО "Рога и Копыта"'), '2020-01-01');
    END IF;

    IF (SELECT COUNT(*) FROM DepartmentEvent) = 0 THEN
        INSERT INTO DepartmentEvent (DepartmentID, EventID, AssignmentDate, ResponsibilityLevel) VALUES
        ((SELECT ID FROM Department WHERE Name = 'Отдел разработки'), (SELECT ID FROM Event WHERE Name = 'Проверить пожарные извещатели в корпусе А'), '2025-12-01', 'Ответственное'),
        ((SELECT ID FROM Department WHERE Name = 'Отдел охраны труда'), (SELECT ID FROM Event WHERE Name = 'Провести инструктаж по пожарной безопасности'), '2025-12-05', 'Ответственное');
    END IF;

    IF (SELECT COUNT(*) FROM EventControl) = 0 THEN
        INSERT INTO EventControl (EmployeeID, EventID, ControlStartDate, Frequency) VALUES
        ((SELECT ID FROM Employee WHERE FullName = 'Федоров Ф.Ф.'), (SELECT ID FROM Event WHERE Name = 'Провести инструктаж по пожарной безопасности'), '2025-12-05', 'Еженедельно');
    END IF;

    IF (SELECT COUNT(*) FROM DocumentSigning) = 0 THEN
        INSERT INTO DocumentSigning (EmployeeID, DocumentID, SigningDate, SignStatus) VALUES
        ((SELECT ID FROM Employee WHERE FullName = 'Петров П.П.'), (SELECT ID FROM Document WHERE Number = 'П-2025-001'), '2025-12-02', 'Подписан');
    END IF;
END $$;