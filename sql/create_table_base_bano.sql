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

CREATE TABLE IF NOT EXISTS cumul_adresses (
    geometrie       geometry ,
    numero          character varying (15),
    voie_cadastre   character varying (300),
    voie_bal        character varying (300),
    voie_osm        character varying (300),
    voie_autre      text,
    voie_fantoir    character varying (300),
    fantoir         character varying (10),
    insee_com       character           (5),
    cadastre_com    character varying (10),
    dept            character varying (3),
    code_postal     text,
    source          character varying (100),
    batch_import_id integer);

CREATE INDEX IF NOT EXISTS cumul_adresses_fantoir ON cumul_adresses(fantoir);
CREATE INDEX IF NOT EXISTS cumul_adresses_fantoir_source_idx ON cumul_adresses(fantoir, source);
CREATE INDEX IF NOT EXISTS cumul_adresses_geo ON cumul_adresses USING gist (geometrie);
CREATE INDEX IF NOT EXISTS cumul_adresses_insee ON cumul_adresses(insee_com) WITH (fillfactor=95);
CREATE INDEX IF NOT EXISTS cumul_adresses_dept ON cumul_adresses(dept) WITH (fillfactor=95);
CREATE INDEX IF NOT EXISTS cumul_adresses_source ON cumul_adresses(source) WITH (fillfactor=95);
CREATE INDEX IF NOT EXISTS cumul_adresses_insee_source ON cumul_adresses(insee_com,source) WITH (fillfactor=95);

CREATE TABLE IF NOT EXISTS cumul_voies
(   geometrie       geometry ,
    voie_cadastre   character varying (300),
    voie_bal        character varying (300),
    voie_osm        character varying (300),
    voie_autre      text,
    voie_fantoir    character varying (300),
    fantoir         character varying (10),
    insee_com       character           (5),
    cadastre_com    character varying (10),
    dept            character varying (3),
    code_postal     text,
    source          character varying (100),
    voie_index      integer,
    batch_import_id integer);

CREATE INDEX IF NOT EXISTS    cumul_voies_fantoir ON cumul_voies(fantoir);
CREATE INDEX IF NOT EXISTS    cumul_voies_fantoir_source_idx ON cumul_voies(fantoir, source);
CREATE INDEX IF NOT EXISTS    cumul_voies_geo ON cumul_voies USING gist (geometrie);
CREATE INDEX IF NOT EXISTS    cumul_voies_insee ON cumul_voies(insee_com) WITH (fillfactor=95);
CREATE INDEX IF NOT EXISTS    cumul_voies_dept ON cumul_voies(dept) WITH (fillfactor=95);
CREATE INDEX IF NOT EXISTS    cumul_voies_source ON cumul_voies(source) WITH (fillfactor=95);
CREATE INDEX IF NOT EXISTS    cumul_voies_insee_source ON cumul_voies(insee_com,source) WITH (fillfactor=95);

ALTER TABLE cumul_voies CLUSTER ON cumul_voies_insee;

CREATE TABLE IF NOT EXISTS cumul_places
(   geometrie       geometry ,
    libelle_cadastre    character varying (300),
    libelle_osm     character varying (300),
    libelle_fantoir character varying (300),
    ld_bati         integer,
    ld_osm          character varying (30),
    fantoir         character varying (10),
    insee_com       character           (5),
    -- cadastre_com    character varying (10),
    dept            character varying (3),
    code_postal     text,
    source          character varying (100),
    batch_import_id integer);

CREATE INDEX IF NOT EXISTS cumul_places_geo ON cumul_places USING GIST(geometrie);
CREATE INDEX IF NOT EXISTS cumul_places_insee_com ON cumul_places (insee_com);

ALTER TABLE cumul_places CLUSTER ON cumul_places_insee_com;

CREATE TABLE IF NOT EXISTS batch (
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

CREATE TABLE IF NOT EXISTS batch_historique (
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

CREATE TABLE IF NOT EXISTS code_cadastre (
        dept character varying(3),
        cadastre_dept character (3),
        nom_com character varying(250),
        cadastre_com character(5),
        insee_com character(5),
        code_postal character(5),
        format_cadastre character varying(10),
        date_maj integer);

CREATE TABLE IF NOT EXISTS tmp_code_cadastre
AS SELECT * FROM code_cadastre LIMIT 0;

-- CREATE TABLE IF NOT EXISTS suffixe (
--                 geometrie               geometry,
--                 insee_com               character(5),
--                 libelle_suffixe character varying(100)
-- );
-- CREATE INDEX IF NOT EXISTS gidx_suffixe ON suffixe USING GIST(geometrie);

/*CREATE TABLE IF NOT EXISTS type_voie (
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
*/
