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
WHERE	p.insee_com = '#com__'	AND
		b.wall = 'yes';

/*CREATE TEMP TABLE	noms_insee
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
*/
CREATE TEMP TABLE	noms_fantoir
AS
SELECT	code_insee||id_voie||cle_rivoli fantoir,
		libelle_voie,
		lieud_dit_bati
FROM	fantoir_voie
WHERE	code_insee = '#com__'	AND
		type_voie = '3';

DELETE FROM	cumul_places
WHERE 		source = 'CADASTRE'	AND
			insee_com = '#com__';

INSERT INTO cumul_places (insee_com,libelle_cadastre,source,fantoir,geometrie)
SELECT	p.insee_com,
		p.voie_cadastre,
		'CADASTRE',
		coalesce(n.fantoir,null),
		coalesce(ST_Transform(ST_Centroid(ST_Collect(b.geometrie)),4326),ST_Transform(ST_Centroid(ST_Collect(p.geometrie)),4326))
FROM	parcelles p
LEFT OUTER JOIN buildings_noms b
ON		p.voie_cadastre = b.voie_cadastre
JOIN	noms_fantoir n
--LEFT OUTER JOIN	noms_fantoir n
ON		trim(both from substr(p.voie_cadastre,1,26)) = n.libelle_voie
WHERE p.insee_com = '#com__'
GROUP BY 1,2,3,4;

COMMIT;