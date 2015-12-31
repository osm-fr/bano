TRUNCATE TABLE tmp_code_cadastre;
\copy tmp_code_cadastre (dept,cadastre_dept,nom_com,code_postal,cadastre_com,format_cadastre) FROM './code_cadastre.csv' WITH CSV DELIMITER ','
UPDATE tmp_code_cadastre SET insee_com = dept||substr(cadastre_com,3,3) WHERE length(dept) = 2;
UPDATE tmp_code_cadastre SET insee_com = dept||substr(cadastre_com,4,2) WHERE length(dept) = 3;
UPDATE tmp_code_cadastre SET date_maj = (SELECT to_char(n,'YYMMDD')::integer FROM (SELECT now() AS n)a);

DELETE FROM code_cadastre
WHERE insee_com IN (SELECT insee_com FROM tmp_code_cadastre WHERE format_cadastre = 'VECT' AND nom_com != ''
						INTERSECT
						SELECT insee_com FROM code_cadastre WHERE format_cadastre = 'IMAG');
DELETE FROM code_cadastre
WHERE insee_com IN (SELECT insee_com
					FROM (SELECT insee_com,cadastre_com FROM tmp_code_cadastre WHERE format_cadastre = 'VECT' AND nom_com != ''
						EXCEPT
						SELECT insee_com,cadastre_com FROM code_cadastre)i);
INSERT INTO code_cadastre
SELECT t.*
FROM tmp_code_cadastre t
LEFT OUTER JOIN code_cadastre c
ON t.insee_com = c.insee_com
WHERE c.insee_com IS NULL AND
		t.nom_com != '';
--SELECT 	*
--FROM 	code_cadastre
--WHERE 	date_maj = (SELECT to_char(n,'YYMMDD')::integer FROM (SELECT now() AS n)a)
--ORDER BY 2,3;
--SELECT DISTINCT dept
--FROM    code_cadastre
--WHERE   date_maj = (SELECT to_char(n,'YYMMDD')::integer FROM (SELECT now() AS n)a)
--ORDER BY 1;
