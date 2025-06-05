# Агент, который проверяет код аэропорта и выводит результат
Этот агент проверяет код аэропорта и возвращает выходную структуру.

**Класс действия:**
action_find_international_airport

**Параметры:**
1. input_XML - входный XML-пример.
2. working_structure - структура, получаемая от 1-го агента.

**Рабочий процесс:**
- Агент, сравнивая между собой коды аэропортов отправления и прибытия, проверяет их на соответствие и формирует выходную структуру используя входную структуру.

XML-пример из первого агента:

![image](https://github.com/user-attachments/assets/b6f32892-f345-4b3c-9d30-a42928cba0d0)

Пример входной структуры:

![image](https://github.com/user-attachments/assets/5862ea62-f3cf-4557-bcb7-939297be8517)

### Логические правила агента

![image](https://github.com/user-attachments/assets/fecc7526-ad4d-428d-b4f9-dbb17845fa71)

![image](https://github.com/user-attachments/assets/f1ac8ce0-f7dc-4178-a9ff-236b65fb93ff)

### Результат
Возможные коды результата:
* `SC_RESULT_OK` — выходная структура сформирована.
* `SC_RESULT_ERROR` — внутренняя ошибка.
