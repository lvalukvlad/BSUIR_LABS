CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    summary TEXT NOT NULL DEFAULT '',
    source_file TEXT UNIQUE,
    doc_len INTEGER NOT NULL DEFAULT 0,
    detected_language TEXT,
    result_json JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS training_texts (
    id SERIAL PRIMARY KEY,
    language TEXT NOT NULL,
    text TEXT NOT NULL,
    source_file TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS language_profiles (
    id SERIAL PRIMARY KEY,
    language TEXT NOT NULL,
    lexeme TEXT NOT NULL,
    frequency FLOAT NOT NULL DEFAULT 0,
    method TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS documents_lang_idx ON documents (detected_language);
CREATE INDEX IF NOT EXISTS training_lang_idx ON training_texts (language);
CREATE INDEX IF NOT EXISTS profiles_lang_idx ON language_profiles (language);

CREATE TABLE IF NOT EXISTS search_logs (
    id SERIAL PRIMARY KEY,
    query TEXT NOT NULL,
    normalized TEXT NOT NULL DEFAULT '',
    results_count INTEGER NOT NULL DEFAULT 0,
    elapsed_ms INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);