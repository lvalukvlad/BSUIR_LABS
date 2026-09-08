# Агент, который проверяет код аэропорта и выводит результат
Этот агент проверяет код аэропорта и возвращает выходную структуру.

**Класс действия:**
action_find_international_flight

**Параметры:**
1. input_XML - входный XML-пример.
2. working_structure - структура, получаемая от 1-го агента.
3. rules_set - набор логических правил.

**Рабочий процесс:**
- Агент, сравнивая между собой коды аэропортов отправления и прибытия, проверяет их на соответствие и формирует выходную структуру используя входную структуру.

XML-пример из первого агента:

![image](https://github.com/user-attachments/assets/5862ea62-f3cf-4557-bcb7-939297be8517)

### Логические правила агента

![image](https://github.com/user-attachments/assets/fecc7526-ad4d-428d-b4f9-dbb17845fa71)

![image](https://github.com/user-attachments/assets/f1ac8ce0-f7dc-4178-a9ff-236b65fb93ff)

Примеры выходных структур:

![image](https://github.com/user-attachments/assets/97142d66-b5e2-463e-8a77-5d144d2745bb)

![image](https://github.com/user-attachments/assets/1182c2f2-3834-44f5-a67a-e0ca53487c67)


### Результат
Возможные коды результата:
* `SC_RESULT_OK` — выходная структура сформирована.
* `SC_RESULT_ERROR` — внутренняя ошибка.
