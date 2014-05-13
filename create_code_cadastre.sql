DROP TABLE IF EXISTS code_cadastre CASCADE;
CREATE TABLE code_cadastre (
	dept character varying(3),
        cadastre_dept character (3),
	nom_com character varying(250),
	cadastre_com character(5),
	insee_com character(5),
	code_postal character(5),
	format_cadastre character varying(10));
\copy code_cadastre (dept,cadastre_dept,nom_com,code_postal,cadastre_com,format_cadastre) FROM './code_cadastre.csv' WITH CSV DELIMITER ','
UPDATE code_cadastre set insee_com = dept||substr(cadastre_com,3,3) WHERE length(dept) = 2;
UPDATE code_cadastre set insee_com = dept||substr(cadastre_com,4,2) WHERE length(dept) = 3;

