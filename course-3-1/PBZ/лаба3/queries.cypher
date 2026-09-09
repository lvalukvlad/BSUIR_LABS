-- 1: Получить все документы заданного типа (например, "Приказ") и их мероприятия.
MATCH (dt:EventType {typeName: "Приказ"})<-[:OF_TYPE]-(d:Document)-[:HAS_EVENT]->(e:Event)
RETURN d.number AS documentNumber, e.name AS eventName, e.deadline AS eventDeadline, e.isCompleted AS eventIsCompleted
ORDER BY d.number, e.deadline

-- 2: Найти все невыполненные мероприятия, дедлайн которых <= текущей даты (на "сегодня").
MATCH (e:Event)
WHERE e.deadline <= date() AND e.isCompleted = false
OPTIONAL MATCH (e)-[:ASSIGNED_TO]->(emp:Employee)
RETURN e.name AS eventName, e.deadline AS eventDeadline, d.number AS documentNumber, emp.fullName AS assignedEmployee
MATCH (d:Document)-[:HAS_EVENT]->(e)
ORDER BY e.deadline

-- 3: Получить список сотрудников, назначенных на мероприятия в документе с определённым номером (например, "П-2025-001").
MATCH (d:Document {number: "П-2025-001"})-[:HAS_EVENT]->(e:Event)-[:ASSIGNED_TO]->(emp:Employee)
RETURN d.number AS documentNumber, e.name AS eventName, emp.fullName AS employeeName, emp.position AS employeePosition
ORDER BY e.name, emp.fullName

-- 4: Найти все мероприятия, назначенные на определённого сотрудника (например, "Федоров Ф.Ф.").
MATCH (emp:Employee {fullName: "Федоров Ф.Ф."})<-[:ASSIGNED_TO]-(e:Event)<-[:HAS_EVENT]-(d:Document)
RETURN emp.fullName AS employeeName, d.number AS documentNumber, e.name AS eventName, e.deadline AS eventDeadline, e.isCompleted AS eventIsCompleted
ORDER BY e.deadline

-- 5: Получить автора (корреспондента) документа с определённым номером (например, "Р-2025-001").
MATCH (d:Document {number: "Р-2025-001"})-[:AUTHORED_BY]->(c:Correspondent)
RETURN d.number AS documentNumber, c.fullName AS authorFullName, c.position AS authorPosition

-- 6: Найти все документы, автор которых работает в определённом подразделении (например, "Отдел разработки").
MATCH (dep:Department {name: "Отдел разработки"})<-[:WORKS_IN]-(c:Correspondent)<-[:AUTHORED_BY]-(d:Document)
RETURN dep.name AS departmentName, c.fullName AS authorFullName, d.number AS documentNumber, d.creationDate AS documentCreationDate
ORDER BY c.fullName, d.creationDate

-- 7: Получить список всех мероприятий за определённый период (например, с 2025-12-01 по 2025-12-20).
MATCH (e:Event)
WHERE e.deadline >= date("2025-12-01") AND e.deadline <= date("2025-12-20")
OPTIONAL MATCH (e)<-[:HAS_EVENT]-(d:Document)
RETURN e.name AS eventName, e.deadline AS eventDeadline, e.isCompleted AS eventIsCompleted, d.number AS documentNumber
ORDER BY e.deadline, d.number

-- 8: Найти все подразделения, в которых работают сотрудники, назначеные на мероприятия, связанные с документом "П-2025-001".
MATCH (d:Document {number: "П-2025-001"})-[:HAS_EVENT]->(e:Event)-[:ASSIGNED_TO]->(emp:Employee)-[:WORKS_IN]->(dep:Department)
RETURN DISTINCT dep.name AS departmentName, collect(emp.fullName) AS employeesInDepartmentAssignedToDocEvents
ORDER BY dep.name

-- 9: Получить иерархию подразделений (родительские и дочерние).
MATCH (parent:Department)
OPTIONAL MATCH (parent)<-[:BELONGS_TO]-(child:Department)
RETURN parent.name AS parentDepartmentName, child.name AS childDepartmentName
ORDER BY parent.name, child.name

-- 10: Найти мероприятия, у которых дедлайн <= сегодня, и которые не назначены ни на одного сотрудника.
MATCH (e:Event)
WHERE e.deadline <= date() AND e.isCompleted = false
OPTIONAL MATCH (e)-[:ASSIGNED_TO]->(emp:Employee)
WITH e, emp
WHERE emp IS NULL
OPTIONAL MATCH (e)<-[:HAS_EVENT]-(d:Document)
RETURN e.name AS eventName, e.deadline AS eventDeadline, d.number AS documentNumber
ORDER BY e.deadline, d.number
