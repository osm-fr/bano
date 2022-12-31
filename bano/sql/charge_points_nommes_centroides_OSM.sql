WITH
lignes_brutes
AS
(SELECT l.way,
        unnest(array[l.name,l.tags->'alt_name',l.tags->'old_name']) AS name,
        COALESCE(a9.code_insee,'xxxxx') as insee_jointure,
        a9.code_insee insee_ac,
        unnest(array["ref:FR:FANTOIR","ref:FR:FANTOIR:left","ref:FR:FANTOIR:right"]) AS fantoir,
        ST_Within(l.way,p.way)::integer as within
FROM    (SELECT way FROM planet_osm_polygon WHERE "ref:INSEE" = '__code_insee__') p
JOIN    planet_osm_line l
ON      ST_Intersects(l.way, p.way)
LEFT OUTER JOIN (SELECT * FROM polygones_insee_a9 WHERE insee_a8 = '__code_insee__') a9
ON      ST_Intersects(l.way, a9.geometrie)
WHERE   (l.highway != '' OR
        l.waterway = 'dam')     AND
        l.name != ''),
lignes_noms
AS
(SELECT *
FROM    lignes_brutes
WHERE   name IS NOT NULL AND
        (fantoir LIKE '__code_insee__%' OR fantoir = '')),
lignes_noms_rang
AS
(SELECT *,
        RANK() OVER(PARTITION BY name,insee_ac ORDER BY within DESC) rang
FROM    lignes_noms),
lignes_agregees
AS
(SELECT ST_LineMerge(ST_Collect(way)) way,
        name,
        insee_ac,
        insee_jointure,
        fantoir
FROM    lignes_noms_rang
WHERE   rang = 1
GROUP BY 2,3,4,5),
centroide_lignes_agregees
AS
(SELECT ST_Centroid(ST_LineMerge(ST_Collect(way))) way,
        name,
        insee_ac,
        insee_jointure,
        fantoir
FROM    lignes_noms_rang
WHERE   rang = 1
GROUP BY 2,3,4,5),
resultat
AS
(SELECT ST_SetSRID(ST_ClosestPoint(lignes_agregees.way,centroide_lignes_agregees.way),4326) point,
        lignes_agregees.name,
        lignes_agregees.insee_ac,
        lignes_agregees.fantoir
FROM    lignes_agregees
JOIN    centroide_lignes_agregees
USING   (name,insee_jointure))
SELECT  ST_x(point),
        ST_y(point),
        name,
        insee_ac,
        fantoir
FROM    resultat;
