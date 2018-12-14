WITH
fantoir 
AS
(SELECT DISTINCT code_insee||id_voie||cle_rivoli AS fantoir,
TRIM(BOTH FROM nature_voie||' '||libelle_voie)   AS nom
FROM fantoir_voie
WHERE code_insee = '__com__' AND
      type_voie = '3'),
lieux_dits
AS
(SELECT ST_Centroid(geometrie) AS geometrie,
        nom,
        insee_com
FROM lieux_dits
WHERE insee_com = '__com__'),
mix
AS
(SELECT l.*,f.fantoir
FROM lieux_dits l LEFT OUTER JOIN fantoir f
USING (nom))
SELECT ST_X(geometrie),
		ST_Y(geometrie),
		nom,
		fantoir,
		null,
		insee_com
FROM	mix;
