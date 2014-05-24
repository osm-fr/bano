\set dp '\'%' :dept '%\''
/*SELECT 		dept,
		etape,
		source,
		sum(nombre_adresses)"nb adresses"
FROM		batch
WHERE           dept like :dp
GROUP BY	1,2,3
ORDER BY	1,2 DESC,3;
*/
SELECT 	c.dept,
	CASE
		WHEN coalesce(re.nb,0) = c.vect THEN c.vect::character varying
		ELSE coalesce(re.nb,0)||' / '||c.vect
	END Recuperes,
	coalesce(ac.nb,0) "Addr Cadastre",
	coalesce(ao.nb,0) "Addr OSM"
FROM	(SELECT	DISTINCT dept,
		count(*)vect
	FROM 	code_cadastre
	WHERE 	dept like :dp AND
		format_cadastre = 'VECT' 
	GROUP BY 1) c
LEFT OUTER JOIN
	(SELECT dept,
		sum(nombre_adresses)*-1 nb
	FROM 	batch
	WHERE 	source = 'CADASTRE'	AND
		etape = 'recupCadastre'
	GROUP BY 1) re
	ON 	c.dept = re.dept
LEFT OUTER JOIN
	(SELECT dept,
		sum(nombre_adresses) nb
	FROM 	batch
	WHERE 	source = 'CADASTRE'	AND
		etape = 'loadCumul' GROUP BY 1) ac
	ON 	c.dept = ac.dept
LEFT OUTER JOIN
	(SELECT dept,
		sum(nombre_adresses) nb
	FROM 	batch 
	WHERE 	source = 'OSM'	AND
		etape = 'loadCumul'
	GROUP BY 1) ao
	ON 	c.dept = ao.dept
ORDER BY 1;

