CREATE TABLE IF NOT EXISTS documents (
    id              SERIAL PRIMARY KEY,
    title           TEXT NOT NULL,
    body            TEXT NOT NULL,
    language        TEXT NOT NULL,
    domain          TEXT NOT NULL,
    source_file     TEXT UNIQUE,
    char_len        INTEGER NOT NULL DEFAULT 0,
    summary_classic TEXT NOT NULL DEFAULT '',
    keywords_json   JSONB NOT NULL DEFAULT '[]',
    network_json    JSONB NOT NULL DEFAULT '[]',
    selected_json   JSONB NOT NULL DEFAULT '[]',
    elapsed_ms      INTEGER NOT NULL DEFAULT 0,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS doc_terms (
    doc_id  INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    term    TEXT NOT NULL,
    tf      INTEGER NOT NULL,
    weight  DOUBLE PRECISION NOT NULL,
    PRIMARY KEY (doc_id, term)
);

CREATE TABLE IF NOT EXISTS global_terms (
    term TEXT PRIMARY KEY,
    df   INTEGER NOT NULL
);
