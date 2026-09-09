-- Документы коллекции и статистика, необходимая вероятностной модели ранжирования.
CREATE TABLE IF NOT EXISTS documents (
    id          SERIAL PRIMARY KEY,
    title       TEXT NOT NULL,
    body        TEXT NOT NULL,
    summary     TEXT NOT NULL DEFAULT '',
    source_file TEXT UNIQUE,
    doc_len     INTEGER NOT NULL DEFAULT 0,
    created_at  TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Словарь коллекции: термин в нормальной форме и его документная частота.
CREATE TABLE IF NOT EXISTS terms (
    id   SERIAL PRIMARY KEY,
    term TEXT NOT NULL UNIQUE,
    df   INTEGER NOT NULL DEFAULT 0
);

-- Инвертированный индекс: сколько раз термин встретился в документе.
CREATE TABLE IF NOT EXISTS postings (
    term_id INTEGER NOT NULL REFERENCES terms(id) ON DELETE CASCADE,
    doc_id  INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    tf      INTEGER NOT NULL,
    PRIMARY KEY (term_id, doc_id)
);

CREATE INDEX IF NOT EXISTS postings_doc_idx ON postings (doc_id);
CREATE INDEX IF NOT EXISTS terms_prefix_idx ON terms (term text_pattern_ops);

-- Журнал поисковых запросов пользователя.
CREATE TABLE IF NOT EXISTS search_logs (
    id            SERIAL PRIMARY KEY,
    query         TEXT NOT NULL,
    normalized    TEXT NOT NULL DEFAULT '',
    results_count INTEGER NOT NULL DEFAULT 0,
    elapsed_ms    INTEGER NOT NULL DEFAULT 0,
    created_at    TIMESTAMP NOT NULL DEFAULT NOW()
);
