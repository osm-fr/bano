WITH
lignes_ac
AS
(SELECT b.nom,
        COALESCE(a9.code_insee,'xxxxx') as insee_jointure,
        a9.code_insee insee_ac,
        a9.nom nom_ac,
        b.geometrie
FROM    (SELECT * FROM commune_filaire WHERE code_insee = '__code_insee__')b
LEFT OUTER JOIN (SELECT * FROM polygones_insee_a9 WHERE insee_a8 = '__code_insee__') a9
ON      ST_Intersects(b.geometrie, a9.geometrie)),
resultat
AS
(SELECT ST_ClosestPoint(geometrie,ST_Centroid(geometrie)) AS geometrie,
       nom,
       insee_ac,
       nom_ac
FROM   lignes_ac)
SELECT ST_X(geometrie),
       ST_Y(geometrie),
       nom,
       NULL::text,
       insee_ac,
       nom_ac
FROM   resultat;