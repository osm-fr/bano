CREATE TEMP TABLE	buildings_noms
AS
SELECT	b.geometrie,	
		b.wall,
		p.insee_com,
		p.voie_cadastre
FROM	buildings b
JOIN	parcelles p
ON	p.geometrie && b.geometrie	AND
	ST_Contains(p.geometrie,st_centroid(b.geometrie))
WHERE	p.insee_com = '#com__';

CREATE TEMP TABLE	noms_insee
AS
SELECT	voie_cadastre,
		insee_com
FROM	parcelles
WHERE	insee_com = '#com__'	AND
		voie_cadastre != ''
EXCEPT
SELECT	voie_cadastre,
		insee_com
FROM	parcelles
WHERE	insee_com = '#com__'	AND
		numero != '';
 
DELETE FROM	cumul_places
WHERE 		source = 'CADASTRE'	AND
			insee_com = '#com__';

INSERT INTO cumul_places (insee_com,libelle_cadastre,source,geometrie)
SELECT	b.insee_com,
		b.voie_cadastre,
		'CADASTRE',
		ST_Transform(ST_Centroid(ST_Collect(geometrie)),4326)
FROM	buildings_noms b
JOIN	noms_insee n
ON		b.voie_cadastre = n.voie_cadastre	AND
		b.insee_com = n.insee_com
WHERE	b.wall = 'yes'
GROUP BY 1,2,3;

COMMIT;