-- Эталонные запросы и разметка релевантности (qrels) для оценки качества поиска.
CREATE TABLE IF NOT EXISTS eval_queries (
    id      SERIAL PRIMARY KEY,
    code    TEXT NOT NULL UNIQUE,
    query   TEXT NOT NULL,
    comment TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS eval_qrels (
    query_id    INTEGER NOT NULL REFERENCES eval_queries(id) ON DELETE CASCADE,
    source_file TEXT NOT NULL,
    relevance   INTEGER NOT NULL DEFAULT 1,
    PRIMARY KEY (query_id, source_file)
);

-- Сохранённые прогоны оценки качества: позволяют сравнивать модели ранжирования.
CREATE TABLE IF NOT EXISTS eval_runs (
    id         SERIAL PRIMARY KEY,
    model      TEXT NOT NULL,
    top_k      INTEGER NOT NULL,
    summary    JSONB NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
