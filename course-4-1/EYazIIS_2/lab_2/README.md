# Лабораторная работа 2. Автоматическое распознавание языка текста

Вариант 13: Русский, Немецкий | PDF | Коротких слов, Частотных слов, Нейросетевой

```
eyaziis-lab-2/              корень лабораторной
├── README.md
├── Лабораторная работа 2.pdf
├── demo-pdf/               демонстрационные PDF (ru/de)
├── eyaziis-lab-2/          программная часть (Docker Compose)
└── eyazis-report-2/        отчёт LaTeX
```

## Что нужно установить

- Docker Desktop
- MiKTeX с `latexmk`
- Java (для диаграмм PlantUML)

## Запуск системы

```powershell
cd eyaziis-lab-2
docker compose up --build
```

Интерфейс: <http://localhost:8080>
API: <http://localhost:8000/docs>

Демонстрационные PDF для загрузки: каталог `demo-pdf` (два русских и два немецких текста).

Остановка: `docker compose down`. Том базы сохраняется; чтобы начать с пустой коллекции: `docker compose down -v`.

### Полезные команды внутри контейнера

```powershell
docker compose exec backend python -m app.scenarios
docker compose exec backend python -m app.evaluator --export /out/png --json /out/png/metrics.json
```

Графики метрик пишутся в `../eyazis-report-2/png/`.

## Сборка отчёта

```powershell
cd eyazis-report-2
powershell -ExecutionPolicy Bypass -File .\scripts\render-diagrams.ps1
latexmk -pdf -interaction=nonstopmode course_report.tex
```

## Методы распознавания

1. **Метод коротких слов** — ПОЯ из лексем ≤5 символов
2. **Метод частотных слов** — ПОЯ из топ-50 самых частотных слов
3. **Нейросетевой метод** — MLPClassifier на N-граммных признаках (N=1..5)

## Источник

Совместная работа: https://github.com/Kukrynitza/BSUIR (ветка `course-4-semester-1`, путь `course-4-semester-1/EYAZIIS/eyaziis-lab-2`).