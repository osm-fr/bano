DROP TABLE IF EXISTS cumul_adresses CASCADE;
CREATE TABLE cumul_adresses
(	geometrie		geometry ,
	numero 			character varying (15),
	voie_cadastre	character varying (300),
	voie_osm		character varying (300),
	voie_fantoir	character varying (300),
	fantoir			character varying (10),
	insee_com		character 			(5),
	cadastre_com	character varying (10),
	dept			character varying (3),
	code_postal		character varying (5),
	source			character varying (100),
	batch_import_id	integer);

DROP TABLE IF EXISTS cumul_places CASCADE;
CREATE TABLE cumul_places
(	geometrie		geometry ,
	libelle_cadastre	character varying (300),
	libelle_osm		character varying (300),
	libelle_fantoir	character varying (300),
	fantoir			character varying (10),
	insee_com		character 			(5),
	cadastre_com	character varying (10),
	dept			character varying (3),
	code_postal		character varying (5),
	source			character varying (100),
	batch_import_id	integer);

CREATE INDEX cumul_places_geo ON cumul_places USING GIST(geometrie);
CREATE INDEX cumul_places_insee_com ON cumul_places (insee_com);

DROP TABLE IF EXISTS batch CASCADE;
CREATE TABLE batch
(	id_batch 		serial,
	source			character varying (100),
	etape			character varying (100),
	timestamp_debut	float,
	date_debut		character varying (100),
	date_fin		character varying (100),
	dept			character varying (3),
	cadastre_com	character (5),
	nom_com			character varying(250),
	nombre_adresses	integer);

DROP TABLE IF EXISTS batch_historique CASCADE;
CREATE TABLE batch_historique
(       id_batch                integer,
 	source			character varying (100),
	etape			character varying (100),
	timestamp_debut	float,
	date_debut		character varying (100),
	date_fin		character varying (100),
	dept			character varying (3),
	cadastre_com	character (5),
	nom_com			character varying(250),
	nombre_adresses	integer);

DROP TABLE IF EXISTS code_cadastre CASCADE;
CREATE TABLE code_cadastre (
        dept character varying(3),
        cadastre_dept character (3),
        nom_com character varying(250),
        cadastre_com character(5),
        insee_com character(5),
        code_postal character(5),
        format_cadastre character varying(10),
		date_maj integer);

DROP TABLE IF EXISTS tmp_code_cadastre CASCADE;
CREATE TABLE tmp_code_cadastre
AS SELECT * FROM code_cadastre LIMIT 0;

DROP TABLE IF EXISTS suffixe CASCADE;
CREATE TABLE suffixe (
                geometrie               geometry,
                insee_com               character(5),
                libelle_suffixe character varying(100)
);
CREATE INDEX gidx_suffixe
ON suffixe
USING GIST(geometrie);

DROP TABLE IF EXISTS parcelles CASCADE;
CREATE TABLE parcelles (
		geometrie 		geometry,
		insee_com 		character(5),
		id_cadastre		character varying(15),
		numero 			character varying (15),
		voie_cadastre	character varying (300),
		fantoir			character varying (10)
);
CREATE INDEX parcelles_insee_com
ON parcelles(insee_com);

DROP TABLE IF EXISTS buildings CASCADE;
CREATE TABLE buildings (
		geometrie 		geometry,
		id_building		serial,
		insee_com 		character(5),
		wall			character varying (3)
);
CREATE INDEX buildings_insee_com
ON buildings(insee_com);

DROP TABLE IF EXISTS parcelles_noms CASCADE;
CREATE TABLE parcelles_noms (
		geometrie 		geometry,
		insee_com 		character(5),
		libelle		 	character varying(100),
		fantoir			character varying (10)
);
CREATE INDEX parcelles_noms_insee_com
ON parcelles_noms(insee_com);