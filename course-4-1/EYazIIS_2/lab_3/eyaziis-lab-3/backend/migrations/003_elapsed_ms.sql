ALTER TABLE documents
    ALTER COLUMN elapsed_ms TYPE DOUBLE PRECISION
    USING elapsed_ms::double precision;
