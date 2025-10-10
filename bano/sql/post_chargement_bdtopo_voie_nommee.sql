ALTER TABLE bdtopo_voie_nommee RENAME COLUMN insee_commune TO code_insee;

CREATE INDEX idx_bdtopo_voie_nommee_code_insee ON bdtopo_voie_nommee (code_insee);
