DROP TABLE IF EXISTS cumul_adresses CASCADE;
CREATE TABLE cumul_adresses
(	geometrie		geometry ,
	numero 			character varying (15),
	voie_cadastre	character varying (300),
	voie_osm		character varying (300),
	fantoir			character varying (10),
	insee_com		character 			(5),
	cadastre_com	character varying (10),
	dept			character varying (3),
	code_postal		character varying (5),
	source			character varying (100),
	batch_import_id	integer);

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
