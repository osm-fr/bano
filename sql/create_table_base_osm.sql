CREATE TABLE IF NOT EXISTS fantoir_voie (
                            code_dept       character(3),
                            code_dir        character(1),
                            code_com        character(3),
                            code_insee      character(5),
                            id_voie         character(4),
                            fantoir         character(9),
                            fantoir10       character(10),
                            cle_rivoli      character(1),
                            nature_voie     character varying(4),
                            libelle_voie    character varying(26),
                            type_commune    character(1),
                            caractere_rur   character(1),
                            caractere_voie  character(1),
                            caractere_pop   character(1),
                            pop_a_part      integer,
                            pop_fictive     integer,
                            caractere_annul character(1),
                            date_annul      character varying(9),
                            date_creation   character varying(9),
                            code_majic      character(5),
                            type_voie       character(1),
                            ld_bati         character(1),
                            dernier_mot     character varying(8));
CREATE INDEX IF NOT EXISTS idx_fantoir_voie_dept  ON fantoir_voie(code_dept);
CREATE INDEX IF NOT EXISTS idx_fantoir_code_insee ON fantoir_voie(code_insee);
CREATE INDEX IF NOT EXISTS idx_fantoir_fantoir    ON fantoir_voie(fantoir);
CREATE INDEX IF NOT EXISTS idx_fantoir_fantoir10  ON fantoir_voie(fantoir10);

CREATE TABLE IF NOT EXISTS ban_odbl (
    id text,
    id_fantoir text,
    numero  text,
    rep text,
    nom_voie text,
    code_postal text,
    code_insee text,
    nom_commune text,
    code_insee_ancienne_commune text,
    nom_ancienne_commune text,
    x float,
    y float,
    lon float,
    lat float,
    alias text,
    nom_ld text,
    libelle_acheminement text,
    nom_afnor text,
    source_position text,
    source_nom_voie text);
--    geometrie geometry (Point, 4326) DEFAULT (ST_Point(lon,lat)));
CREATE INDEX IF NOT EXISTS idx_ban_odbl_code_insee ON ban_odbl(code_insee);


CREATE TABLE IF NOT EXISTS bal_cadastre (
    cle_interop text,
    uid_adresse text,
    numero  text,
    suffixe text,
    pseudo_numero boolean,
    voie_nom text,
    voie_code text,
    code_postal text,
    libelle_acheminement text,
    destination_principale text,
    commune_code text,
    commune_nom text,
    source text,
    long float,
    lat float,
    x float,
    y float,
    position text,
    date_der_maj date);
CREATE INDEX IF NOT EXISTS idx_bal_cadastre_commune_code ON bal_cadastre(commune_code);
CREATE INDEX IF NOT EXISTS idx_bal_cadastre_commune_codedestination_principale ON bal_cadastre(commune_code,destination_principale);

CREATE TABLE IF NOT EXISTS bal_locales (
    cle_interop text,
    commune_code text,
    commune_nom text,
    voie_code text,
    voie_nom text,
    numero  text,
    suffixe text,
    long float,
    lat float,
    license text);
CREATE INDEX IF NOT EXISTS idx_bal_open_data_commune_code ON bal_locales(commune_code);

CREATE TABLE IF NOT EXISTS lieux_dits (
        insee_com       character(5),
        nom        text,
        created date,
        updated date,
        geometrie geometry(Polygon,4326)
);
CREATE INDEX IF NOT EXISTS lieux_dits_insee_com ON lieux_dits(insee_com);
CREATE INDEX IF NOT EXISTS gidx_lieux_dits      ON lieux_dits USING gist (geometrie);

CREATE TABLE IF NOT EXISTS parcelles_noms (
        geometrie       geometry,
        insee_com       character(5),
        libelle         character varying(100),
        fantoir         character varying (10)
);
CREATE INDEX IF NOT EXISTS parcelles_noms_insee_com ON parcelles_noms(insee_com);

CREATE TABLE IF NOT EXISTS type_voie (
        id_voie integer,
        tag_value text,
        tag_index integer);
TRUNCATE TABLE type_voie; 
INSERT INTO type_voie (id_voie,tag_value) 
    VALUES (1,'steps'),
            (2,'path'),
            (3,'cycleway'),
            (4,'footway'),
            (5,'pedestrian'),
            (6,'track'),
            (7,'service'),
            (8,'road'),
            (9,'living_street'),
            (10,'residential'),
            (11,'unclassified'),
            (12,'tertiary'),
            (13,'secondary'),
            (14,'primary'),
            (15,'trunk'),
            (16,'motorway');
UPDATE type_voie SET tag_index = power(2,id_voie-1);


CREATE TABLE IF NOT EXISTS type_highway_insee (
        name          text,
        highway       text,
        insee_com     character(5),
        timestamp_maj integer DEFAULT (date_part('epoch'::text, CURRENT_TIMESTAMP))::integer
);
CREATE INDEX IF NOT EXISTS idx_type_highway_insee_insee_com ON type_highway_insee(insee_com);

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
        timestamp_maj integer DEFAULT (date_part('epoch'::text, CURRENT_TIMESTAMP))::integer
);
CREATE INDEX IF NOT EXISTS idx_place_insee_insee_com ON place_insee(insee_com);

CREATE TABLE IF NOT EXISTS cadastre_2_place (
        geometrie geometry(Point, 4326),
        nom           text,
        fantoir       text,
        insee_com     character(5)
);
CREATE INDEX IF NOT EXISTS gidx_cadastre_2_place ON cadastre_2_place USING GIST(geometrie);
CREATE INDEX IF NOT EXISTS idx_cadastre_2_place_insee_com ON cadastre_2_place(insee_com);

CREATE TABLE IF NOT EXISTS expire_tiles (
  z integer,
  x integer,
  y integer,
  geometrie geometry(Polygon, 3857)
);
CREATE INDEX IF NOT EXISTS gidx_expire_tiles ON expire_tiles(geometrie);

GRANT SELECT ON ALL TABLES IN SCHEMA public TO public;