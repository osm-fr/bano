DROP TABLE IF EXISTS cumul_adresses CASCADE;
CREATE TABLE cumul_adresses
(	geometrie		geometry ,
	numero 			character varying (10),
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
	"timestamp"		float,
	date_en_clair		character varying (100),
	cadastre_com		character (5),
	nombre_adresses		integer);

DROP TABLE IF EXISTS batch_historique CASCADE;
CREATE TABLE batch_historique
(       id_batch                integer,
        source          	character varying (100),
        "timestamp"             float,
        date_en_clair           character varying (100),
        cadastre_com            character (5),
        nombre_adresses         integer);

