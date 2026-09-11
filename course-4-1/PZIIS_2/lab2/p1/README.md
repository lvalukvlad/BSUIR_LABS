# Часть 1 — Secure Notes Lab

Учебное веб-приложение: регистрация, вход, CRUD заметок (неконфиденциальные) и секретов (конфиденциальные, Fernet), выход.

## Запуск

```bash
cd lab2/p1/app
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Откройте http://127.0.0.1:5050

Опционально:
```bash
export LAB2_SECRET_KEY='длинная-случайная-строка'
export LAB2_HTTPS=1   # если есть HTTPS — Secure cookie
```

## Функции

| Действие | Маршрут |
|----------|---------|
| Регистрация | `/register` |
| Вход | `/login` |
| Выход | `POST /logout` |
| Заметки CRUD + поиск | `/notes` |
| Секреты CRUD + поиск | `/secrets` |

## Меры защиты (кратко)

- хеш пароля PBKDF2-SHA256;
- сессии HttpOnly + SameSite;
- CSRF-токен на изменяющих запросах;
- ORM / параметризованные запросы;
- изоляция данных по `user_id`;
- шифрование тела секретов (Fernet) на диске;
- приложение слушает только `127.0.0.1`.
