CREATE TABLE IF NOT EXISTS suffixe (
                geometrie               geometry,
                insee_com               character(5),
                libelle_suffixe character varying(100)
);
CREATE INDEX IF NOT EXISTS gidx_suffixe ON suffixe USING GIST(geometrie);
