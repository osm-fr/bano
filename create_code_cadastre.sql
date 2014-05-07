DROP TABLE IF EXISTS code_cadastre CASCADE;
CREATE TABLE code_cadastre (
	dept character(3),
	cadastre_com character(5),
	insee_com character(5),
	nom_com character varying(250));
\copy code_cadastre (dept,cadastre_com,nom_com) FROM './code_cadastre.txt' WITH CSV DELIMITER ' '
UPDATE code_cadastre set insee_com = substr(dept,2,2)||substr(cadastre_com,3,3) WHERE dept like '0%';
UPDATE code_cadastre set insee_com = dept||substr(cadastre_com,4,2) WHERE dept like '9%';

