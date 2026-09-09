-- 1. Функция создания документа
CREATE OR REPLACE FUNCTION CreateDocument(
    p_number VARCHAR(50),
    p_creation_date DATE,
    p_release_date DATE,
    p_content TEXT,
    p_document_type_id INT, -- Изменено
    p_signer_position VARCHAR(100),
    p_signer_full_name VARCHAR(100)
)
RETURNS INT
LANGUAGE plpgsql
AS
$$
DECLARE
    new_id INT;
BEGIN
    INSERT INTO Document (Number, CreationDate, ReleaseDate, Content, DocumentTypeID, SignerPosition, SignerFullName)
    VALUES (p_number, p_creation_date, p_release_date, p_content, p_document_type_id, p_signer_position, p_signer_full_name)
    RETURNING ID INTO new_id;

    RETURN new_id;
END;
$$;

-- 2. Процедура редактирования документа
CREATE OR REPLACE PROCEDURE UpdateDocument(
    p_document_id INT,
    p_number VARCHAR(50),
    p_creation_date DATE,
    p_release_date DATE,
    p_content TEXT,
    p_document_type_id INT,
    p_signer_position VARCHAR(100),
    p_signer_full_name VARCHAR(100)
)
LANGUAGE plpgsql
AS
$$
BEGIN
    UPDATE Document
    SET Number = p_number,
        CreationDate = p_creation_date,
        ReleaseDate = p_release_date,
        Content = p_content,
        DocumentTypeID = p_document_type_id, -- Изменено
        SignerPosition = p_signer_position,
        SignerFullName = p_signer_full_name
    WHERE ID = p_document_id;
END;
$$;

-- 3. Функция создания мероприятия
CREATE OR REPLACE FUNCTION CreateEvent(
    p_name VARCHAR(200),
    p_deadline DATE,
    p_completion_date DATE DEFAULT NULL,
    p_is_completed BOOLEAN DEFAULT FALSE
)
RETURNS INT
LANGUAGE plpgsql
AS
$$
DECLARE
    new_id INT;
BEGIN
    INSERT INTO Event (Name, Deadline, CompletionDate, IsCompleted)
    VALUES (p_name, p_deadline, p_completion_date, p_is_completed)
    RETURNING ID INTO new_id;

    RETURN new_id;
END;
$$;

-- 4. Процедура редактирования мероприятия
CREATE OR REPLACE PROCEDURE UpdateEvent(
    p_event_id INT,
    p_name VARCHAR(200),
    p_deadline DATE,
    p_completion_date DATE DEFAULT NULL,
    p_is_completed BOOLEAN DEFAULT FALSE
)
LANGUAGE plpgsql
AS
$$
BEGIN
    UPDATE Event
    SET Name = p_name,
        Deadline = p_deadline,
        CompletionDate = p_completion_date,
        IsCompleted = p_is_completed
    WHERE ID = p_event_id;
END;
$$;

-- 5. Процедура добавления связи документа и корреспондента
CREATE OR REPLACE PROCEDURE AddDocumentCorrespondent(
    p_correspondent_id INT,
    p_document_id INT,
    p_author_assignment_date DATE
)
LANGUAGE plpgsql
AS
$$
BEGIN
    INSERT INTO DocumentCorrespondent (CorrespondentID, DocumentID, AuthorAssignmentDate)
    VALUES (p_correspondent_id, p_document_id, p_author_assignment_date)
    ON CONFLICT (CorrespondentID, DocumentID) DO NOTHING;
END;
$$;

-- 6. Процедура добавления мероприятия к документу
CREATE OR REPLACE PROCEDURE AddEventToDocument(
    p_document_id INT,
    p_event_id INT,
    p_sequence_number INT
)
LANGUAGE plpgsql
AS
$$
BEGIN
    INSERT INTO DocumentEvent (DocumentID, EventID, SequenceNumber)
    VALUES (p_document_id, p_event_id, p_sequence_number)
    ON CONFLICT (DocumentID, EventID) DO NOTHING;
END;
$$;

-- 7. Процедура поручения мероприятия сотруднику
CREATE OR REPLACE PROCEDURE AssignEventToEmployee(
    p_event_id INT,
    p_employee_id INT,
    p_assignment_date DATE,
    p_priority VARCHAR(50)
)
LANGUAGE plpgsql
AS
$$
BEGIN
    INSERT INTO EventAssignment (EventID, EmployeeID, AssignmentDate, Priority)
    VALUES (p_event_id, p_employee_id, p_assignment_date, p_priority)
    ON CONFLICT (EventID, EmployeeID) DO NOTHING;
END;
$$;

-- 8. Функция для получения списка невыполненных мероприятий на заданную дату
CREATE OR REPLACE FUNCTION GetUncompletedEventsByDate(
    p_target_date DATE
)
RETURNS TABLE (
    DocumentNumber VARCHAR(50),
    EventName VARCHAR(200),
    Deadline DATE,
    CompletionDate DATE,
    IsCompleted BOOLEAN,
    CorrespondentFullName VARCHAR(100),
    CorrespondentPosition VARCHAR(100),
    DepartmentName VARCHAR(100),
    DocumentReleaseDate DATE --
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        d.Number as DocumentNumber,
        e.Name as EventName,
        e.Deadline,
        e.CompletionDate,
        e.IsCompleted,
        c.FullName as CorrespondentFullName,
        c.Position as CorrespondentPosition,
        dep.Name as DepartmentName,
        d.ReleaseDate as DocumentReleaseDate
    FROM Event e
    INNER JOIN DocumentEvent de ON e.ID = de.EventID
    INNER JOIN Document d ON de.DocumentID = d.ID
    INNER JOIN DocumentCorrespondent dc ON d.ID = dc.DocumentID
    INNER JOIN Correspondent c ON dc.CorrespondentID = c.ID
    INNER JOIN CorrespondentDepartment cd ON c.ID = cd.CorrespondentID
    INNER JOIN Department dep ON cd.DepartmentID = dep.ID
    INNER JOIN DocumentType dt ON d.DocumentTypeID = dt.ID
    WHERE e.Deadline <= p_target_date
          AND e.IsCompleted = FALSE
    ORDER BY e.Deadline, d.Number;
END;
$$;

-- 9. Функция для получения списка мероприятий за период
CREATE OR REPLACE FUNCTION GetEventsByPeriod(
    p_start_date DATE,
    p_end_date DATE
)
RETURNS TABLE (
    EventName VARCHAR(200),
    Deadline DATE,
    CompletionDate DATE,
    IsCompleted BOOLEAN,
    DocumentNumber VARCHAR(50),
    DocumentTypeName VARCHAR(50)
)
LANGUAGE plpgsql
AS
$$
BEGIN
    RETURN QUERY
    SELECT
        e.Name as EventName,
        e.Deadline,
        e.CompletionDate,
        e.IsCompleted,
        d.Number as DocumentNumber,
        dt.TypeName as DocumentTypeName
    FROM Event e
    INNER JOIN DocumentEvent de ON e.ID = de.EventID
    INNER JOIN Document d ON de.DocumentID = d.ID
    INNER JOIN DocumentType dt ON d.DocumentTypeID = dt.ID
    WHERE e.Deadline BETWEEN p_start_date AND p_end_date
    ORDER BY e.Deadline, d.Number;
END;
$$;

-- 10. Функция для получения документов по типу на текущую дату
CREATE OR REPLACE FUNCTION GetDocumentsByTypeCurrentDate(
    p_document_type_name VARCHAR(50)
)
RETURNS TABLE (
    CompanyName VARCHAR(100),
    CurrentDate DATE,
    DocumentTypeName VARCHAR(50),
    DocumentNumber VARCHAR(50),
    CreationDate DATE,
    IsCompleted BOOLEAN
)
LANGUAGE plpgsql
AS
$$
BEGIN
    RETURN QUERY
    SELECT
        comp.Name as CompanyName,
        CURRENT_DATE as CurrentDate,
        dt.TypeName as DocumentTypeName,
        d.Number as DocumentNumber,
        d.CreationDate,
        EXISTS (
            SELECT 1
            FROM DocumentEvent de
            INNER JOIN Event e ON de.EventID = e.ID
            WHERE de.DocumentID = d.ID AND e.IsCompleted = FALSE
        ) as IsCompleted
    FROM Document d
    INNER JOIN DocumentType dt ON d.DocumentTypeID = dt.ID
    CROSS JOIN Company comp
    WHERE dt.TypeName = p_document_type_name
      AND d.CreationDate <= CURRENT_DATE
    ORDER BY d.CreationDate DESC, d.Number;
END;
$$;

-- 11. Триггер для автоматического обновления статуса выполнения мероприятия
CREATE OR REPLACE FUNCTION UpdateEventCompletionStatus()
RETURNS TRIGGER
LANGUAGE plpgsql
AS
$$
BEGIN
    IF NEW.CompletionDate IS NOT NULL AND OLD.CompletionDate IS NULL THEN
        NEW.IsCompleted := TRUE;
    ELSIF NEW.CompletionDate IS NULL AND OLD.CompletionDate IS NOT NULL THEN
        NEW.IsCompleted := FALSE;
    END IF;

    RETURN NEW;
END;
$$;

-- 12. Триггер для автоматического обновления статуса выполнения мероприятия
CREATE TRIGGER EventCompletionStatusTrigger
    BEFORE UPDATE ON Event
    FOR EACH ROW
    EXECUTE FUNCTION UpdateEventCompletionStatus();

-- 13. Триггер для проверки дат документа
CREATE OR REPLACE FUNCTION CheckDocumentDates()
RETURNS TRIGGER
LANGUAGE plpgsql
AS
$$
BEGIN
    IF NEW.ReleaseDate < NEW.CreationDate THEN
        RAISE EXCEPTION 'Дата выхода документа не может быть раньше даты создания';
    END IF;

    RETURN NEW;
END;
$$;

-- 14. Триггер для проверки дат документа
CREATE TRIGGER DocumentDatesCheckTrigger
    BEFORE INSERT OR UPDATE ON Document
    FOR EACH ROW
    EXECUTE FUNCTION CheckDocumentDates();

-- 15. Процедура для массового добавления мероприятий к документу
CREATE OR REPLACE PROCEDURE AddEventsArrayToDocument(
    p_document_id INT,
    p_event_ids INT[],
    p_sequence_numbers INT[]
)
LANGUAGE plpgsql
AS
$$
DECLARE
    i INT;
    event_id INT;
BEGIN
    IF NOT EXISTS (SELECT 1 FROM Document WHERE ID = p_document_id) THEN
        RAISE EXCEPTION 'Документ с ID % не существует', p_document_id;
    END IF;

    FOR i IN 1..array_length(p_event_ids, 1)
    LOOP
        event_id := p_event_ids[i];

        IF NOT EXISTS (SELECT 1 FROM Event WHERE ID = event_id) THEN
            RAISE NOTICE 'Мероприятие с ID % не существует, пропускаем', event_id;
            CONTINUE;
        END IF;

        INSERT INTO DocumentEvent (DocumentID, EventID, SequenceNumber)
        VALUES (p_document_id, event_id, p_sequence_numbers[i])
        ON CONFLICT (DocumentID, EventID) DO NOTHING;
    END LOOP;
END;
$$;

-- 16. Функция для получения всех исполнителей мероприятия
CREATE OR REPLACE FUNCTION GetEventExecutors(
    p_event_id INT
)
RETURNS TABLE (
    EmployeeID INT,
    FullName VARCHAR(100),
    EmployeePosition VARCHAR(100),
    AssignmentDate DATE,
    Priority VARCHAR(50)
)
LANGUAGE plpgsql
AS
$$
BEGIN
    RETURN QUERY
    SELECT
        e.ID as EmployeeID,
        e.FullName,
        e.Position as EmployeePosition,
        ea.AssignmentDate,
        ea.Priority
    FROM Employee e
    INNER JOIN EventAssignment ea ON e.ID = ea.EmployeeID
    WHERE ea.EventID = p_event_id
    ORDER BY ea.Priority, ea.AssignmentDate;
END;
$$;

-- 17. Функция создания сотрудника
CREATE OR REPLACE FUNCTION CreateEmployee(
    p_full_name VARCHAR(100),
    p_position VARCHAR(100)
)
RETURNS INT
LANGUAGE plpgsql
AS
$$
DECLARE
    new_id INT;
BEGIN
    INSERT INTO Employee (FullName, Position)
    VALUES (p_full_name, p_position)
    RETURNING ID INTO new_id;

    RETURN new_id;
END;
$$;

-- 18. Процедура редактирования сотрудника
CREATE OR REPLACE PROCEDURE UpdateEmployee(
    p_employee_id INT,
    p_full_name VARCHAR(100),
    p_position VARCHAR(100)
)
LANGUAGE plpgsql
AS
$$
BEGIN
    UPDATE Employee
    SET FullName = p_full_name,
        Position = p_position
    WHERE ID = p_employee_id;
END;
$$;

-- 19. Функция создания корреспондента
CREATE OR REPLACE FUNCTION CreateCorrespondent(
    p_full_name VARCHAR(100),
    p_position VARCHAR(100)
)
RETURNS INT
LANGUAGE plpgsql
AS
$$
DECLARE
    new_id INT;
BEGIN
    INSERT INTO Correspondent (FullName, Position)
    VALUES (p_full_name, p_position)
    RETURNING ID INTO new_id;

    RETURN new_id;
END;
$$;

-- 20. Процедура назначения сотрудника в подразделение
CREATE OR REPLACE PROCEDURE AssignEmployeeToDepartment(
    p_employee_id INT,
    p_department_id INT,
    p_start_date DATE,
    p_status VARCHAR(50)
)
LANGUAGE plpgsql
AS
$$
BEGIN
    INSERT INTO EmployeeDepartment (EmployeeID, DepartmentID, StartDate, Status)
    VALUES (p_employee_id, p_department_id, p_start_date, p_status)
    ON CONFLICT (EmployeeID, DepartmentID) DO UPDATE
    SET StartDate = EXCLUDED.StartDate,
        Status = EXCLUDED.Status;
END;
$$;

-- 21. Функция создания типа документа
CREATE OR REPLACE FUNCTION CreateDocumentType(
    p_type_name VARCHAR(50)
)
RETURNS INT
LANGUAGE plpgsql
AS
$$
DECLARE
    new_id INT;
BEGIN
    INSERT INTO DocumentType (TypeName)
    VALUES (p_type_name)
    ON CONFLICT (TypeName) DO NOTHING
    RETURNING ID INTO new_id;

    RETURN new_id;
END;
$$;

-- 22. Процедура редактирования типа документа
CREATE OR REPLACE PROCEDURE UpdateDocumentType(
    p_type_id INT,
    p_new_type_name VARCHAR(50)
)
LANGUAGE plpgsql
AS
$$
BEGIN
    UPDATE DocumentType
    SET TypeName = p_new_type_name
    WHERE ID = p_type_id;
END;
$$;

-- 23. Процедура удаления типа документа
-- Необходимо проверить, что нет документов этого типа, или обработать их.
CREATE OR REPLACE PROCEDURE DeleteDocumentType(
    p_type_id INT
)
LANGUAGE plpgsql
AS
$$
BEGIN
    IF EXISTS (SELECT 1 FROM Document WHERE DocumentTypeID = p_type_id) THEN
        RAISE EXCEPTION 'Невозможно удалить тип документа с ID %: существуют документы этого типа.', p_type_id;
    END IF;

    DELETE FROM DocumentType WHERE ID = p_type_id;
END;
$$;
