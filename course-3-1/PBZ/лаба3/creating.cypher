// --- 1. Удаляем ВСЕ существующие узлы и связи ---
MATCH (n) DETACH DELETE n;

// --- 2. Создаём узлы Company ---
CREATE (c1:Company {name: "ООО \"Рога и Копыта\"", legalAddress: "г. Минск, ул. Тестовая, д. 1"});

// --- 3. Создаём узлы Department ---
CREATE (dep_admin:Department {name: "Администрация", hierarchyLevel: 1}),
       (dep_dev:Department {name: "Отдел разработки", hierarchyLevel: 2}),
       (dep_hr:Department {name: "Отдел кадров", hierarchyLevel: 2}),
       (dep_safety:Department {name: "Отдел охраны труда", hierarchyLevel: 2});

// --- 4. Создаём связи иерархии между подразделениями ---
MATCH (parent:Department {name: "Администрация"})
MATCH (child:Department {name: "Отдел разработки"})
MERGE (child)-[:BELONGS_TO]->(parent);

MATCH (parent:Department {name: "Администрация"})
MATCH (child:Department {name: "Отдел кадров"})
MERGE (child)-[:BELONGS_TO]->(parent);

MATCH (parent:Department {name: "Администрация"})
MATCH (child:Department {name: "Отдел охраны труда"})
MERGE (child)-[:BELONGS_TO]->(parent);

// --- 5. Связываем подразделения с компанией ---
MATCH (d:Department)
WHERE d.name IN ["Администрация", "Отдел разработки", "Отдел кадров", "Отдел охраны труда"]
MATCH (c:Company {name: "ООО \"Рога и Копыта\""})
MERGE (d)-[:PART_OF]->(c);

// --- 6. Создаём узлы EventType ---
CREATE (et_order:EventType {typeName: "Приказ"}),
       (et_directive:EventType {typeName: "Распоряжение"}),
       (et_instruction:EventType {typeName: "Указание"});

// --- 7. Создаём узлы Correspondent ---
CREATE (corr_petrov:Correspondent {fullName: "Петров П.П.", position: "Генеральный директор"}),
       (corr_ivanov:Correspondent {fullName: "Иванов И.И.", position: "Главный инженер"}),
       (corr_sidorov:Correspondent {fullName: "Сидоров С.С.", position: "Начальник отдела разработки"}),
       (corr_kozlova:Correspondent {fullName: "Козлова К.К.", position: "Начальник отдела кадров"});

// --- 8. Создаём узлы Employee ---
CREATE (emp_mikhailov:Employee {fullName: "Михайлов М.М.", position: "Ведущий инженер"}),
       (emp_fedorov:Employee {fullName: "Федоров Ф.Ф.", position: "Специалист"}),
       (emp_alekseev:Employee {fullName: "Алексеев А.А.", position: "Главный специалист"}),
       (emp_egorova:Employee {fullName: "Егорова Е.Е.", position: "Инженер"});

// --- 9. Связываем Correspondent с Department ---
MATCH (c:Correspondent {fullName: "Петров П.П."})
MATCH (d:Department {name: "Администрация"})
MERGE (c)-[:WORKS_IN]->(d);

MATCH (c:Correspondent {fullName: "Иванов И.И."})
MATCH (d:Department {name: "Отдел разработки"})
MERGE (c)-[:WORKS_IN]->(d);

MATCH (c:Correspondent {fullName: "Сидоров С.С."})
MATCH (d:Department {name: "Отдел разработки"})
MERGE (c)-[:WORKS_IN]->(d);

MATCH (c:Correspondent {fullName: "Козлова К.К."})
MATCH (d:Department {name: "Отдел кадров"})
MERGE (c)-[:WORKS_IN]->(d);

// --- 10. Связываем Employee с Department ---
MATCH (e:Employee {fullName: "Михайлов М.М."})
MATCH (d:Department {name: "Отдел разработки"})
MERGE (e)-[:WORKS_IN]->(d);

MATCH (e:Employee {fullName: "Федоров Ф.Ф."})
MATCH (d:Department {name: "Отдел разработки"})
MERGE (e)-[:WORKS_IN]->(d);

MATCH (e:Employee {fullName: "Алексеев А.А."})
MATCH (d:Department {name: "Отдел кадров"})
MERGE (e)-[:WORKS_IN]->(d);

MATCH (e:Employee {fullName: "Егорова Е.Е."})
MATCH (d:Department {name: "Отдел охраны труда"})
MERGE (e)-[:WORKS_IN]->(d);

// --- 11. Создаём узлы Document ---
CREATE (doc_order_001:Document {number: "П-2025-001", creationDate: date("2025-12-01"), releaseDate: date("2025-12-02"), content: "Утвердить план мероприятий по повышению пожарной безопасности на 2025 год.", signerPosition: "Генеральный директор", signerFullName: "Петров П.П."}),
       (doc_directive_001:Document {number: "Р-2025-001", creationDate: date("2025-12-05"), releaseDate: date("2025-12-05"), content: "Назначить ответственных за проверку пожарного оборудования.", signerPosition: "Главный инженер", signerFullName: "Иванов И.И."}),
       (doc_instruction_001:Document {number: "У-2025-001", creationDate: date("2025-12-10"), releaseDate: date("2025-12-10"), content: "О введении в действие нового регламента.", signerPosition: "Начальник отдела разработки", signerFullName: "Сидоров С.С."});

// --- 12. Связываем Document с EventType ---
MATCH (d:Document {number: "П-2025-001"})
MATCH (et:EventType {typeName: "Приказ"})
MERGE (d)-[:OF_TYPE]->(et);

MATCH (d:Document {number: "Р-2025-001"})
MATCH (et:EventType {typeName: "Распоряжение"})
MERGE (d)-[:OF_TYPE]->(et);

MATCH (d:Document {number: "У-2025-001"})
MATCH (et:EventType {typeName: "Указание"})
MERGE (d)-[:OF_TYPE]->(et);

// --- 13. Связываем Document с Correspondent ---
MATCH (d:Document {number: "П-2025-001"})
MATCH (c:Correspondent {fullName: "Петров П.П."})
MERGE (d)-[:AUTHORED_BY]->(c);

MATCH (d:Document {number: "Р-2025-001"})
MATCH (c:Correspondent {fullName: "Иванов И.И."})
MERGE (d)-[:AUTHORED_BY]->(c);

MATCH (d:Document {number: "У-2025-001"})
MATCH (c:Correspondent {fullName: "Сидоров С.С."})
MERGE (d)-[:AUTHORED_BY]->(c);

// --- 14. Создаём узлы Event ---
CREATE (ev_check_alarm: Event {name: "Проверить пожарные извещатели в корпусе А", deadline: date("2025-12-15"), completionDate: date("2025-12-14"), isCompleted: true}),
       (ev_conduct_training: Event {name: "Провести инструктаж по пожарной безопасности", deadline: date("2025-12-18"), completionDate: null, isCompleted: false}), // Просрочено (17.12.2025)
       (ev_prepare_report: Event {name: "Подготовить отчет по проверке охраны труда", deadline: date("2025-12-20"), completionDate: null, isCompleted: false}), // В будущем
       (ev_update_instructions: Event {name: "Обновить инструкции по охране труда", deadline: date("2025-12-10"), completionDate: date("2025-12-10"), isCompleted: true}),
       (ev_assign_responsibles: Event {name: "Назначить ответственных за оборудование", deadline: date("2025-12-06"), completionDate: date("2025-12-06"), isCompleted: true}),
       (ev_familiarize_staff: Event {name: "Ознакомить персонал с новым регламентом", deadline: date("2025-12-11"), completionDate: null, isCompleted: false}); // Просрочено (17.12.2025)

// --- 15. Связываем Document с Event ---
MATCH (d:Document {number: "П-2025-001"})
MATCH (e:Event {name: "Проверить пожарные извещатели в корпусе А"})
MERGE (d)-[:HAS_EVENT]->(e);

MATCH (d:Document {number: "П-2025-001"})
MATCH (e:Event {name: "Провести инструктаж по пожарной безопасности"})
MERGE (d)-[:HAS_EVENT]->(e);

MATCH (d:Document {number: "П-2025-001"})
MATCH (e:Event {name: "Подготовить отчет по проверке охраны труда"})
MERGE (d)-[:HAS_EVENT]->(e);

MATCH (d:Document {number: "Р-2025-001"})
MATCH (e:Event {name: "Назначить ответственных за оборудование"})
MERGE (d)-[:HAS_EVENT]->(e);

MATCH (d:Document {number: "У-2025-001"})
MATCH (e:Event {name: "Ознакомить персонал с новым регламентом"})
MERGE (d)-[:HAS_EVENT]->(e);

// --- 16. Связываем Event с Employee ---
MATCH (e:Event {name: "Проверить пожарные извещатели в корпусе А"})
MATCH (emp:Employee {fullName: "Михайлов М.М."})
MERGE (e)-[:ASSIGNED_TO]->(emp);

MATCH (e:Event {name: "Провести инструктаж по пожарной безопасности"})
MATCH (emp:Employee {fullName: "Федоров Ф.Ф."})
MERGE (e)-[:ASSIGNED_TO]->(emp);

MATCH (e:Event {name: "Подготовить отчет по проверке охраны труда"})
MATCH (emp:Employee {fullName: "Алексеев А.А."})
MERGE (e)-[:ASSIGNED_TO]->(emp);

MATCH (e:Event {name: "Назначить ответственных за оборудование"})
MATCH (emp:Employee {fullName: "Егорова Е.Е."})
MERGE (e)-[:ASSIGNED_TO]->(emp);

MATCH (e:Event {name: "Ознакомить персонал с новым регламентом"})
MATCH (emp:Employee {fullName: "Михайлов М.М."})
MERGE (e)-[:ASSIGNED_TO]->(emp);
