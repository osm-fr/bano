ALTER TABLE commune_filaire RENAME COLUMN commune TO code_insee;
CREATE INDEX idx_commune_filaire_code_insee ON commune_filaire (code_insee);