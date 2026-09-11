# Часть 1 — ACL файловой системы (Linux)

Скрипты настраивают пользователей/группы, каталоги `/home/pzs/pzs1x` и набор файлов `file11`…`file55` с правами по методичке, затем проверяют доступ.

## Требования

- Linux с `bash`, `runuser` (пакет `util-linux`)
- Запуск от root: `sudo`

## Порядок работы

```bash
cd lab1/p1
chmod +x *.sh
sudo ./setup.sh
sudo ./verify_files.sh   # п.14 → results/verify_files.*
sudo ./verify_procs.sh   # п.15 → results/verify_procs.*
sudo ./verify_dirs.sh    # п.16 → results/verify_dirs.*
# после сдачи / демонстрации:
sudo ./cleanup.sh        # п.17
```

## Каталоги и владельцы

| Каталог | Режим | Владелец | Смысл |
|---------|-------|----------|--------|
| pzs11 | 700 | iit11:group_iit1 | только владелец |
| pzs12 | 070 | root:group_iit1 | только группа (владелец не iit11 — иначе Unix DAC блокирует группу) |
| pzs13 | 007 | root:root | только остальные |
| pzs14 | 777 | iit11:group_iit1 | все |
| pzs15 | 700 | root:root | только администратор |

## Пользователи

- `group_iit1`: iit11, iit12
- `group_iit2`: iit21, iit22 (`iit21` в `sudo`/`wheel`)
- `iit3` — без этих групп

## Результаты проверки

Файлы в `results/`:

- `verify_files.tsv` / `.txt` — READ/WRITE/EXEC по каждому файлу
- `verify_procs.tsv` / `.txt` — кто смог `kill` процесс filex5
- `verify_dirs.tsv` / `.txt` — list/create/delete по каталогам

Проверки каталогов и записи в файлы **не уничтожают** учебные объекты (используются зонды и откат содержимого).
