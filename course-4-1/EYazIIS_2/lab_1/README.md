# Лабораторная работа 1. Информационно-поисковая система

Вариант 5: интерфейс с пользователем, локальная вычислительная сеть, вероятностная стратегия поиска, русский язык.

```
eyaziis-lab-1/              корень лабораторной
├── README.md
├── eyaziis-lab-1/          программная часть (Docker Compose)
└── eyazis-report-1/        отчёт LaTeX
```

## Что нужно установить

- Docker Desktop (для системы)
- MiKTeX с `latexmk` (для отчёта)
- Java (для диаграмм PlantUML; `plantuml.jar` скачивается скриптом сам)

## Запуск системы

Предварительно запустите Docker Desktop.

```powershell
cd eyaziis-lab-1
docker compose up --build
```

Интерфейс: <http://localhost:8080> (в локальной сети — `http://<IP-узла>:8080`).

API бэкенда доступен и напрямую на <http://localhost:8000/docs>.

Остановка: `docker compose down`. Том базы сохраняется; чтобы начать с пустой коллекции: `docker compose down -v`.

### Полезные команды внутри контейнера

```powershell
docker compose exec backend python -m app.evaluator --export /out/png --json /out/png/metrics.json
docker compose exec backend python scenarios.py
```

Графики метрик пишутся в `../eyazis-report-1/png/`.

## Сборка отчёта

Диаграммы (один раз или после правки `.puml`):

```powershell
cd eyazis-report-1
powershell -ExecutionPolicy Bypass -File .\scripts\render-diagrams.ps1
```

PDF:

```powershell
cd eyazis-report-1
latexmk -pdf -interaction=nonstopmode course_report.tex
```

Результат: `eyazis-report-1/course_report.pdf`.

Очистка вспомогательных файлов: `latexmk -c`.

## Источник

Совместная работа: https://github.com/Kukrynitza/BSUIR (ветка `course-4-semester-1`, путь `course-4-semester-1/EYAZIIS/eyaziis-lab-1`).
