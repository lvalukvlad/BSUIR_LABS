CREATE TABLE IF NOT EXISTS eval_queries (
    id SERIAL PRIMARY KEY,
    code TEXT NOT NULL UNIQUE,
    query TEXT NOT NULL,
    text TEXT NOT NULL,
    relevant TEXT[] NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS eval_runs (
    id SERIAL PRIMARY KEY,
    model TEXT NOT NULL,
    top_k INTEGER NOT NULL,
    summary JSONB NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS recognition_results (
    id SERIAL PRIMARY KEY,
    doc_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    method TEXT NOT NULL,
    language TEXT NOT NULL,
    confidence FLOAT NOT NULL,
    result_json JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);