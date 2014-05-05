DROP TABLE IF EXISTS cumul_adresses CASCADE;
CREATE TABLE cumul_adresses
(	geometrie		geometry (POINT,4326),
	numero 			character varying (10),
	voie_cadastre	character varying (300),
	voie_osm		character varying (300),
	fantoir			character varying (10),
	insee_com		character 			(5),
	cadastre_com	character varying (10),
	dept			character varying (3),
	code_postal		character varying (5),
	fournisseur		character varying (100),
	id_fournisseur	character varying (10),
	batch_import_id	integer);

DROP TABLE IF EXISTS batch CASCADE;
CREATE TABLE batch
(	id_batch 		serial,
	fournisseur		character varying (100),
	"timestamp"		timestamp);
	