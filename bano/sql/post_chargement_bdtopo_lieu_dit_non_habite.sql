ALTER TABLE bdtopo_lieu_dit_non_habite RENAME COLUMN insee_commune TO code_insee;

-- DROP INDEX IF EXISTS idx_bdtopo_lieu_dit_non_habite_code_insee;
CREATE INDEX idx_bdtopo_lieu_dit_non_habite_code_insee ON bdtopo_lieu_dit_non_habite (code_insee);