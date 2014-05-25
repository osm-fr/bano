\set dp '\'%' :dept '%\''
SELECT 	c.dept,
	CASE
		WHEN coalesce(re.nb,0) = c.vect THEN c.vect::character varying
		ELSE coalesce(re.nb,0)||' / '||c.vect
	END "Communes vecteur récupérées",
	coalesce(ac.nb,0) "Adrr Cadastre",
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
--ORDER BY 1
UNION ALL
SELECT  c.dept,
        CASE
                WHEN coalesce(re.nb,0) = c.vect THEN c.vect::character varying
                ELSE coalesce(re.nb,0)||' / '||c.vect
        END Recuperes,
        coalesce(ac.nb,0) "Addr Cadastre",
        coalesce(ao.nb,0) "Addr OSM"
FROM    (SELECT 'France' dept,
                count(*)vect
        FROM    code_cadastre
        WHERE   format_cadastre = 'VECT'
        GROUP BY 1) c
LEFT OUTER JOIN
        (SELECT 'France' dept,
                sum(nombre_adresses)*-1 nb
        FROM    batch
        WHERE   source = 'CADASTRE'     AND
                etape = 'recupCadastre'
        GROUP BY 1) re
        ON      c.dept = re.dept
LEFT OUTER JOIN
        (SELECT 'France' dept,
                sum(nombre_adresses) nb
        FROM    batch
        WHERE   source = 'CADASTRE'     AND
                etape = 'loadCumul' GROUP BY 1) ac
        ON      c.dept = ac.dept
LEFT OUTER JOIN
        (SELECT 'France' dept,
                sum(nombre_adresses) nb
        FROM    batch
        WHERE   source = 'OSM'  AND
                etape = 'loadCumul'
        GROUP BY 1) ao
        ON      c.dept = ao.dept
;

