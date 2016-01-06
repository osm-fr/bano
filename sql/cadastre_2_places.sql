CREATE TEMP TABLE	voie_sans_numero
AS
SELECT insee_com,voie_cadastre
FROM parcelles
WHERE voie_cadastre != '' AND
	insee_com ='__com__' AND
	numero =''
EXCEPT
SELECT insee_com,voie_cadastre
FROM parcelles
WHERE voie_cadastre != '' AND
	insee_com ='__com__' AND
	numero !='';
------------------------------------------------
CREATE TEMP TABLE	t_parcelles
AS
SELECT 	p.insee_com,
	p.voie_cadastre,
	ST_Transform(p.geometrie,4326)geometrie
FROM 	parcelles p
JOIN voie_sans_numero
UsING (insee_com,voie_cadastre)
WHERE p.insee_com ='__com__';
CREATE INDEX ON t_parcelles USING GIST(geometrie);
------------------------------------------------
CREATE TEMP TABLE	t_parcelles_centroide
AS
SELECT 	voie_cadastre,
	insee_com,
	ST_Centroid(ST_Collect(p.geometrie)) geometrie
FROM 	t_parcelles p
GRouP BY 1,2;
CREATE INDEX ON t_parcelles USING GIST(geometrie);
------------------------------------------------
CREATE TEMP TABLE	t_buildings_centroide
AS
SELECT insee_com,
	wall,
	ST_Transform(ST_Centroid(geometrie),4326) geometrie
FROM buildings
WHERE insee_com ='__com__';
CREATE INDEX ON t_buildings_centroide USING GIST(geometrie);
------------------------------------------------
CREATE TEMP TABLE	buildings_noms
AS
(SELECT	b.*,
		p.voie_cadastre
FROM	t_buildings_centroide b
JOIN	t_parcelles p
ON	p.geometrie && b.geometrie	AND
	ST_Contains(p.geometrie,b.geometrie)	AND
	p.insee_com = b.insee_com
WHERE	p.insee_com  ='__com__'	AND
		p.geometrie && b.geometrie AND
		b.wall = 'yes');
------------------------------------------------
CREATE TEMP TABLE	noms_fantoir
AS
(SELECT	code_insee||id_voie||cle_rivoli fantoir,
		libelle_voie,
		ld_bati,
		code_insee
FROM	fantoir_voie
WHERE	code_insee  ='__com__'	AND
		type_voie = '3'	AND
		caractere_annul = '');
------------------------------------------------
CREATE TEMP TABLE	fantoir_voies_1_2
AS
(SELECT code_insee,
		TRIM(BOTH FROM nature_voie||' '||libelle_voie) voie_1_2
FROM	fantoir_voie
WHERE	type_voie in ('1','2') AND
		code_insee  ='__com__'
EXCEPT
SELECT 	code_insee,
		TRIM(BOTH FROM nature_voie||' '||libelle_voie)
FROM	fantoir_voie
WHERE	type_voie in ('3') AND
		code_insee ='__com__');
------------------------------------------------
CREATE TEMP TABLE	mix_parcelles
AS
(SELECT	p.insee_com,
		p.voie_cadastre,
		ld_bati,
		COALESCE(n.fantoir,null) fantoir,
		COALESCE(ST_Centroid(ST_Collect(b.geometrie)),ST_Centroid(ST_Collect(p.geometrie))) geometrie
FROM	t_parcelles_centroide p
LEFT OUTER JOIN buildings_noms b
ON		p.voie_cadastre = b.voie_cadastre AND
		p.insee_com = b.insee_com
LEFT OUTER JOIN	noms_fantoir n
ON		TRIM(BOTH FROM SUBSTR(p.voie_cadastre,1,26)) = n.libelle_voie AND
		p.insee_com = n.code_insee
LEFT OUTER JOIN fantoir_voies_1_2 fv
ON		p.voie_cadastre = fv.voie_1_2 AND
		p.insee_com = fv.code_insee
WHERE	p.insee_com  ='__com__'	AND
--		pn.voie_cadastre IS NULL AND
		fv.code_insee IS NULL
GROUP BY 1,2,3,4);
------------------------------------------------
SELECT ST_X(geometrie),
		ST_Y(geometrie),
		voie_cadastre,
		fantoir,
		ld_bati,
		insee_com
FROM	mix_parcelles;
