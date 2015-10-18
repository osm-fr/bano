WITH	buildings_noms
AS
(SELECT	b.geometrie,	
		b.wall,
		p.insee_com,
		p.voie_cadastre
FROM	buildings b
JOIN	parcelles p
ON	p.geometrie && b.geometrie	AND
	ST_Contains(p.geometrie,st_centroid(b.geometrie))
WHERE	p.insee_com = '#com__'	AND
		b.wall = 'yes'),
noms_fantoir
AS
(SELECT	code_insee||id_voie||cle_rivoli fantoir,
		libelle_voie,
		ld_bati
FROM	fantoir_voie
WHERE	code_insee = '#com__'	AND
		type_voie = '3'	AND
		caractere_annul = '')
SELECT ST_X(geometrie),
		ST_Y(geometrie),
		'',
		voie_cadastre,
		fantoir,
		ld_bati
FROM	(SELECT	p.insee_com,
				p.voie_cadastre,
				ld_bati,
				coalesce(n.fantoir,null) fantoir,
				coalesce(ST_Transform(ST_Centroid(ST_Collect(b.geometrie)),4326),ST_Transform(ST_Centroid(ST_Collect(p.geometrie)),4326)) geometrie
		FROM	parcelles p
		LEFT OUTER JOIN buildings_noms b
		ON		p.voie_cadastre = b.voie_cadastre
		JOIN	noms_fantoir n
		--LEFT OUTER JOIN	noms_fantoir n
		ON		trim(both from substr(p.voie_cadastre,1,26)) = n.libelle_voie
		WHERE p.insee_com = '#com__'
		GROUP BY 1,2,3,4)a;
