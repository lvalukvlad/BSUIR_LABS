# Часть 2 — управление доступом в PostgreSQL

Вариант по методичке: **PostgreSQL**. Скрипты ставят СУБД, создают роли admin/user/guest и проверяют политику.

## Роли

| Учётная запись | Роль | Права |
|----------------|------|--------|
| `admin_user` / `admin_pass` | `admin_role` | полный доступ к схеме `lab_schema` (DML + DDL) |
| `app_user` / `user_pass` | `user_role` | SELECT/INSERT/UPDATE/DELETE, без CREATE/DROP |
| `guest_user` / `guest_pass` | `guest_role` | только SELECT |

Объекты: БД `lab_db`, схема `lab_schema`, таблица `lab_schema.test_table`.

## Порядок работы

```bash
cd lab1/p2
chmod +x *.sh
sudo ./install.sh
sudo ./setup_acl.sh
./verify.sh
# после сдачи:
sudo ./cleanup.sh          # только объекты лабы
# sudo ./cleanup.sh --purge  # + удаление пакетов PostgreSQL
```

## Результаты

`results/verify_acl.txt` и `results/verify_acl.tsv` — матрица операций с пометкой OK/FAIL.

Подключение при проверке идёт на `127.0.0.1` с паролем (`scram-sha-256` или `md5`), правила добавляются в `pg_hba.conf` (бэкап `*.lab1.bak`).
