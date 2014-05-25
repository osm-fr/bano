TRUNCATE TABLE code_cadastre;
\copy code_cadastre (dept,cadastre_dept,nom_com,code_postal,cadastre_com,format_cadastre) FROM './code_cadastre.csv' WITH CSV DELIMITER ','
UPDATE code_cadastre set insee_com = dept||substr(cadastre_com,3,3) WHERE length(dept) = 2;
UPDATE code_cadastre set insee_com = dept||substr(cadastre_com,4,2) WHERE length(dept) = 3;

