# Лабораторная работа №1 (ТиИСПИС)

**Вариант 15.** Предметная область «Музыка».

Формализация фрагментов базы знаний для системы NIKA (OSTIS): структура предметной области, абсолютные и относительные понятия (≥30), экземпляры и фактографические связи.

## Содержимое

| Путь | Назначение |
|------|------------|
| `kb/extra/section_subject_domain_of_music/` | Исходники SCs для `kb/extra` форка NIKA |
| `sources.md` | Открытые источники фактов |
| `scripts/sync_to_nika.sh` | Копирование БЗ в локальный клон NIKA |
| `tiispis-report-1/` | Отчёт (LaTeX, сборка `latexmk -pdf`) |

## Требования методички (кратко)

1. Выбрать уникальную тему (здесь: музыка).
2. Формализовать структуру ПрО (классы объектов исследования и отношения).
3. Описать ≥30 понятий с теоретико-множественными связями, доменами отношений, определениями/примечаниями.
4. Для каждого понятия — ≥1 экземпляр; связать экземпляры относительными понятиями.
5. Протестировать фрагменты в NIKA (граф, контекстное меню).
6. Составить отчёт.
7. Подготовиться к вопросам.
8. Запушить изменения в свой форк на GitHub.

## Локальный запуск NIKA

Клон **не** хранится в git репозитория лаб (см. `labs/.gitignore`). Рекомендуемый путь: `course-4-1/TiISPIS/labs/nika`.

```bash
cd course-4-1/TiISPIS/labs
git clone -b tpis-2023 --recursive https://github.com/ostis-apps/nika nika
# либо форк:
# git clone -b tpis-2023 --recursive https://github.com/<ваш_аккаунт>/nika nika

cd lab1
chmod +x scripts/sync_to_nika.sh
./scripts/sync_to_nika.sh

cd ../nika
docker compose pull
# Сборка БЗ (сервис называется problem-solver; REBUILD_KB=1 также пересобирает при up)
docker compose run --rm --entrypoint "" problem-solver bash -lc \
  'export BINARY_PATH=/nika/bin BUILD_PATH=/nika/build CONFIG_PATH=/nika/nika.ini KB_PATH=../repo.path; /nika/scripts/build_kb.sh'
docker compose up --no-build
```

Интерфейсы: sc-web — `http://localhost:8000`, диалог NIKA — `http://localhost:3033`.

Документация: <https://ostis-apps.github.io/nika/>. Ветка методички: `tpis-2023`.

## Публикация в форк (после проверки)

```bash
# в корне форка nika, после sync_to_nika.sh
git add kb/extra/
git commit -m "feat(kb): музыка"
git push
```

Pull-request в `ostis-apps/nika` — только по решению преподавателя (оценка 9–10).

## Отчёт

```bash
cd tiispis-report-1
./scripts/render-diagrams.sh   # PlantUML → png/
latexmk -pdf course_report.tex
```

## Источники

См. [sources.md](sources.md).
