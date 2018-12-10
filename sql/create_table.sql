CREATE TABLE IF NOT EXISTS :schema_cible.fantoir_voie (
                            code_dept       character(2),
                            code_dir        character(1),
                            code_com        character(3),
                            code_insee      character(5),
                            id_voie         character(4),
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
CREATE INDEX IF NOT EXISTS idx_fantoir_voie_dept  ON      :schema_cible.fantoir_voie(code_dept);
CREATE INDEX IF NOT EXISTS idx_fantoir_code_insee ON      :schema_cible.fantoir_voie(code_insee);

CREATE TABLE IF NOT EXISTS :schema_cible.cumul_adresses (
    geometrie       geometry ,
    numero          character varying (15),
    voie_cadastre   character varying (300),
    voie_osm        character varying (300),
    voie_fantoir    character varying (300),
    fantoir         character varying (10),
    insee_com       character           (5),
    cadastre_com    character varying (10),
    dept            character varying (3),
    code_postal     character varying (5),
    source          character varying (100),
    batch_import_id integer);

CREATE INDEX IF NOT EXISTS cumul_adresses_fantoir ON :schema_cible.cumul_adresses(fantoir);
CREATE INDEX IF NOT EXISTS cumul_adresses_fantoir_source_idx ON :schema_cible.cumul_adresses(fantoir, source);
CREATE INDEX IF NOT EXISTS cumul_adresses_geo ON :schema_cible.cumul_adresses USING gist (geometrie);
CREATE INDEX IF NOT EXISTS cumul_adresses_insee ON :schema_cible.cumul_adresses(insee_com) WITH (fillfactor=95);
CREATE INDEX IF NOT EXISTS cumul_adresses_source ON :schema_cible.cumul_adresses(source) WITH (fillfactor=95);

CREATE TABLE IF NOT EXISTS :schema_cible.cumul_voies
(   geometrie       geometry ,
    voie_cadastre   character varying (300),
    voie_osm        character varying (300),
    voie_fantoir    character varying (300),
    fantoir         character varying (10),
    insee_com       character           (5),
    cadastre_com    character varying (10),
    dept            character varying (3),
    code_postal     character varying (5),
    source          character varying (100),
    voie_index      integer,
    batch_import_id integer);

CREATE INDEX IF NOT EXISTS    cumul_voies_fantoir ON :schema_cible.cumul_voies(fantoir);
CREATE INDEX IF NOT EXISTS    cumul_voies_fantoir_source_idx ON :schema_cible.cumul_voies(fantoir, source);
CREATE INDEX IF NOT EXISTS    cumul_voies_geo ON :schema_cible.cumul_voies USING gist (geometrie);
CREATE INDEX IF NOT EXISTS    cumul_voies_insee ON :schema_cible.cumul_voies(insee_com) WITH (fillfactor=95);
CREATE INDEX IF NOT EXISTS    cumul_voies_source ON :schema_cible.cumul_voies(source) WITH (fillfactor=95);

CREATE TABLE IF NOT EXISTS :schema_cible.cumul_places
(   geometrie       geometry ,
    libelle_cadastre    character varying (300),
    libelle_osm     character varying (300),
    libelle_fantoir character varying (300),
    ld_bati         integer,
    ld_osm          character varying (30),
    fantoir         character varying (10),
    insee_com       character           (5),
    cadastre_com    character varying (10),
    dept            character varying (3),
    code_postal     character varying (5),
    source          character varying (100),
    batch_import_id integer);

CREATE INDEX IF NOT EXISTS cumul_places_geo ON :schema_cible.cumul_places USING GIST(geometrie);
CREATE INDEX IF NOT EXISTS cumul_places_insee_com ON :schema_cible.cumul_places (insee_com);

CREATE TABLE IF NOT EXISTS :schema_cible.batch (
    id_batch        serial,
    source          character varying (100),
    etape           character varying (100),
    timestamp_debut float,
    date_debut      character varying (100),
    date_fin        character varying (100),
    dept            character varying (3),
    cadastre_com    character (5),
    insee_com       character (5),
    nom_com         character varying(250),
    nombre_adresses integer);

CREATE TABLE IF NOT EXISTS :schema_cible.batch_historique (
    id_batch                integer,
    source          character varying (100),
    etape           character varying (100),
    timestamp_debut float,
    date_debut      character varying (100),
    date_fin        character varying (100),
    dept            character varying (3),
    cadastre_com    character (5),
    insee_com       character (5),
    nom_com         character varying(250),
    nombre_adresses integer);

CREATE TABLE IF NOT EXISTS :schema_cible.code_cadastre (
        dept character varying(3),
        cadastre_dept character (3),
        nom_com character varying(250),
        cadastre_com character(5),
        insee_com character(5),
        code_postal character(5),
        format_cadastre character varying(10),
        date_maj integer);

CREATE TABLE IF NOT EXISTS :schema_cible.tmp_code_cadastre
AS SELECT * FROM :schema_cible.code_cadastre LIMIT 0;

CREATE TABLE IF NOT EXISTS :schema_cible.suffixe (
                geometrie               geometry,
                insee_com               character(5),
                libelle_suffixe character varying(100)
);
CREATE INDEX IF NOT EXISTS gidx_suffixe ON :schema_cible.suffixe USING GIST(geometrie);

CREATE TABLE IF NOT EXISTS :schema_cible.parcelles (
        geometrie       geometry,
        insee_com       character(5),
        id_cadastre     character varying(15),
        numero          character varying (15),
        voie_cadastre   character varying (300),
        fantoir         character varying (10)
);
CREATE INDEX IF NOT EXISTS parcelles_insee_com ON :schema_cible.parcelles(insee_com);
CREATE INDEX IF NOT EXISTS gidx_parcelles      ON :schema_cible.parcelles USING gist (geometrie);

CREATE TABLE IF NOT EXISTS :schema_cible.buildings (
        geometrie       geometry,
        id_building     serial,
        insee_com       character(5),
        wall            character varying (3)
);
CREATE INDEX IF NOT EXISTS buildings_insee_com ON :schema_cible.buildings(insee_com);
CREATE INDEX IF NOT EXISTS gidx_buildings      ON :schema_cible.buildings USING gist (geometrie);

CREATE TABLE IF NOT EXISTS :schema_cible.batiments (
        insee_com       character(5),
        nom        character varying(80),
        type_batiment text,
        created date,
        updated date,
        geometrie geometry(MultiPolygon,4326)
);
CREATE INDEX IF NOT EXISTS batiments_insee_com ON :schema_cible.batiments(insee_com);
CREATE INDEX IF NOT EXISTS gidx_batiments      ON :schema_cible.batiments USING gist (geometrie);

CREATE TABLE IF NOT EXISTS :schema_cible.lieux_dits (
        insee_com       character(5),
        nom        character varying(80),
        created date,
        updated date,
        geometrie geometry(MultiPolygon,4326)
);
CREATE INDEX IF NOT EXISTS lieux_dits_insee_com ON :schema_cible.lieux_dits(insee_com);
CREATE INDEX IF NOT EXISTS gidx_lieux_dits      ON :schema_cible.lieux_dits USING gist (geometrie);

CREATE TABLE IF NOT EXISTS :schema_cible.parcelles_noms (
        geometrie       geometry,
        insee_com       character(5),
        libelle         character varying(100),
        fantoir         character varying (10)
);
CREATE INDEX IF NOT EXISTS parcelles_noms_insee_com ON :schema_cible.parcelles_noms(insee_com);

CREATE TABLE IF NOT EXISTS :schema_cible.type_voie (
        id_voie integer,
        tag_value text,
        tag_index integer);
TRUNCATE TABLE :schema_cible.type_voie; 
INSERT INTO :schema_cible.type_voie (id_voie,tag_value) 
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
UPDATE :schema_cible.type_voie SET tag_index = power(2,id_voie-1);

CREATE TABLE IF NOT EXISTS :schema_cible.cadastre_noms_bruts (
        insee_com       character(5),
        voie_cadastre   character varying (300),
        fantoir         character varying (10)
);
CREATE INDEX IF NOT EXISTS idx_cadastre_noms_bruts_insee_com ON :schema_cible.cadastre_noms_bruts(insee_com);