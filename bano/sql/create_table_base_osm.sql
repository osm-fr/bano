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

CREATE TABLE IF NOT EXISTS :schema_cible.bal_cadastre (
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
CREATE INDEX IF NOT EXISTS idx_bal_cadastre_commune_code ON :schema_cible.bal_cadastre(commune_code);

CREATE TABLE IF NOT EXISTS :schema_cible.bal_locales (
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
CREATE INDEX IF NOT EXISTS idx_bal_open_data_commune_code ON :schema_cible.bal_locales(commune_code);

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

/*CREATE TABLE IF NOT EXISTS :schema_cible.cadastre_noms_bruts (
        insee_com       character(5),
        voie_cadastre   character varying (300),
        fantoir         character varying (10)
);
CREATE INDEX IF NOT EXISTS idx_cadastre_noms_bruts_insee_com ON :schema_cible.cadastre_noms_bruts(insee_com);
*/
/*CREATE TABLE IF NOT EXISTS :schema_cible.highway_insee (
        name          text,
        fantoir       text,
        fantoir_left  text,
        fantoir_right text,
        suffixe       text,
        insee_com     character(5),
        timestamp_maj integer DEFAULT (date_part('epoch'::text, CURRENT_TIMESTAMP))::integer
);
CREATE INDEX IF NOT EXISTS idx_highway_insee_insee_com ON :schema_cible.highway_insee(insee_com);*/

CREATE TABLE IF NOT EXISTS :schema_cible.highway_suffixe_insee (
        name          text,
        fantoir       text,
        fantoir_left  text,
        fantoir_right text,
        suffixe       text,
        insee_com     character(5),
        timestamp_maj integer DEFAULT (date_part('epoch'::text, CURRENT_TIMESTAMP))::integer
);
CREATE INDEX IF NOT EXISTS idx_highway_suffixe_insee_insee_com ON :schema_cible.highway_suffixe_insee(insee_com);

CREATE TABLE IF NOT EXISTS :schema_cible.hsnr_insee (
        long          float,
        lat           float,
        provenance    text,
        osm_id        bigint,
        hsnr          text,
        street_name   text,
        tags          hstore,
        suffixe       text,
        insee_com     character(5),
        timestamp_maj integer DEFAULT (date_part('epoch'::text, CURRENT_TIMESTAMP))::integer
);
CREATE INDEX IF NOT EXISTS idx_hsnr_insee_insee_com ON :schema_cible.hsnr_insee(insee_com);

CREATE TABLE IF NOT EXISTS :schema_cible.hsnr_bbox_insee (
        long          float,
        lat           float,
        provenance    text,
        osm_id        bigint,
        hsnr          text,
        street_name   text,
        tags          hstore,
        suffixe       text,
        insee_com     character(5),
        timestamp_maj integer DEFAULT (date_part('epoch'::text, CURRENT_TIMESTAMP))::integer
);
CREATE INDEX IF NOT EXISTS idx_hsnr_bbox_insee_insee_com ON :schema_cible.hsnr_bbox_insee(insee_com);

CREATE TABLE IF NOT EXISTS :schema_cible.hsnr_suffixe_insee (
        long          float,
        lat           float,
        provenance    text,
        osm_id        bigint,
        hsnr          text,
        street_name   text,
        tags          hstore,
        suffixe       text,
        insee_com     character(5),
        timestamp_maj integer DEFAULT (date_part('epoch'::text, CURRENT_TIMESTAMP))::integer
);
CREATE INDEX IF NOT EXISTS idx_hsnr_suffixe_insee_insee_com ON :schema_cible.hsnr_suffixe_insee(insee_com);

CREATE TABLE IF NOT EXISTS :schema_cible.highway_bbox_insee (
        name          text,
        fantoir       text,
        fantoir_left  text,
        fantoir_right text,
        suffixe       text,
        insee_com     character(5),
        timestamp_maj integer DEFAULT (date_part('epoch'::text, CURRENT_TIMESTAMP))::integer
);
CREATE INDEX IF NOT EXISTS idx_highway_bbox_insee_insee_com ON :schema_cible.highway_bbox_insee(insee_com);

CREATE TABLE IF NOT EXISTS :schema_cible.highway_relation_insee (
        name          text,
        tags          hstore,
        insee_com     character(5),
        timestamp_maj integer DEFAULT (date_part('epoch'::text, CURRENT_TIMESTAMP))::integer
);
CREATE INDEX IF NOT EXISTS idx_highway_relation_insee_insee_com ON :schema_cible.highway_relation_insee(insee_com);

CREATE TABLE IF NOT EXISTS :schema_cible.highway_relation_bbox_insee (
        name          text,
        tags          hstore,
        insee_com     character(5),
        timestamp_maj integer DEFAULT (date_part('epoch'::text, CURRENT_TIMESTAMP))::integer
);
CREATE INDEX IF NOT EXISTS idx_highway_relation_bbox_insee_insee_com ON :schema_cible.highway_relation_bbox_insee(insee_com);

CREATE TABLE IF NOT EXISTS :schema_cible.highway_relation_suffixe_insee (
        name          text,
        tags          hstore,
        suffixe       text,
        insee_com     character(5),
        timestamp_maj integer DEFAULT (date_part('epoch'::text, CURRENT_TIMESTAMP))::integer
);
CREATE INDEX IF NOT EXISTS idx_highway_relation_suffixe_insee_insee_com ON :schema_cible.highway_relation_suffixe_insee(insee_com);

CREATE TABLE IF NOT EXISTS :schema_cible.point_par_rue_insee (
        long          float,
        lat           float,
        name          text,
        insee_com     character(5),
        timestamp_maj integer DEFAULT (date_part('epoch'::text, CURRENT_TIMESTAMP))::integer
);
CREATE INDEX IF NOT EXISTS idx_point_par_rue_insee_insee_com ON :schema_cible.point_par_rue_insee(insee_com);

CREATE TABLE IF NOT EXISTS :schema_cible.point_par_rue_complement_insee (
        long          float,
        lat           float,
        name          text,
        fantoir       text,
        suffixe       text,
        insee_com     character(5),
        timestamp_maj integer DEFAULT (date_part('epoch'::text, CURRENT_TIMESTAMP))::integer
);
CREATE INDEX IF NOT EXISTS idx_point_par_rue_complement_insee_insee_com ON :schema_cible.point_par_rue_complement_insee(insee_com);

CREATE TABLE IF NOT EXISTS :schema_cible.type_highway_insee (
        name          text,
        highway       text,
        insee_com     character(5),
        timestamp_maj integer DEFAULT (date_part('epoch'::text, CURRENT_TIMESTAMP))::integer
);
CREATE INDEX IF NOT EXISTS idx_type_highway_insee_insee_com ON :schema_cible.type_highway_insee(insee_com);

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
        long          float,
        lat           float,
        nom           text,
        fantoir       text,
        insee_com     character(5),
        timestamp_maj integer DEFAULT (date_part('epoch'::text, CURRENT_TIMESTAMP))::integer
);
CREATE INDEX IF NOT EXISTS idx_cadastre_2_place_insee_com ON cadastre_2_place(insee_com);
