# Отчёт по лабораторной №1 (ПЗИИС)

LaTeX-отчёт в оформлении БГУИР (тот же каркас, что в `EYazIIS_2/lab_1/eyazis-report-1`): титул, содержание, условные обозначения, разделы, заключение, список источников.

Готовый PDF: [`course_report.pdf`](course_report.pdf) (11 стр.).

## Сборка

```bash
cd lab1/pziis-report-1
latexmk -pdf course_report.tex
```

## Структура

| Файл | Содержание |
|------|------------|
| `cource_title.tex` | Титульный лист |
| `sections/reduction.tex` | Условные обозначения |
| `sections/sec_task.tex` | Постановка задачи |
| `sections/sec_part1.tex` | Часть 1 (ОС / ACL) |
| `sections/sec_part2.tex` | Часть 2 (PostgreSQL) |
| `sections/final.tex` | Заключение и источники |

На титуле: группа **321701**, студенты **И. А. Политыко** и **В. А. Лукашов**, руководитель **Д. А. Сальников**.
