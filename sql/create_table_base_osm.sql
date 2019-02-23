CREATE TABLE IF NOT EXISTS suffixe (
                geometrie               geometry,
                insee_com               character(5),
                libelle_suffixe character varying(100)
);
CREATE INDEX IF NOT EXISTS gidx_suffixe ON suffixe USING GIST(geometrie);

CREATE TABLE IF NOT EXISTS place_insee (
        long          float,
        lat           float,
        place         text,
        name          text,
        fantoir       text,
        ld_bati       text,
        tags          hstore,
        insee_com     character(5),
        timestamp_maj integer
);
CREATE INDEX IF NOT EXISTS idx_place_insee_insee_com ON place_insee(insee_com);

CREATE TABLE IF NOT EXISTS cadastre_2_place (
        long          float,
        lat           float,
        nom           text,
        fantoir       text,
        insee_com     character(5),
        timestamp_maj integer
);
CREATE INDEX IF NOT EXISTS idx_cadastre_2_place_insee_com ON cadastre_2_place(insee_com);
