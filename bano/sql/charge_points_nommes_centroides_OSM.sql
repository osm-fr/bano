WITH
lignes_brutes
AS
(SELECT l.way,
        unnest(array[l.name,l.tags->'alt_name',l.tags->'old_name']) AS name,
        COALESCE(a9.code_insee,'xxxxx') as insee_jointure,
        a9.code_insee insee_ac,
        unnest(array["ref:FR:FANTOIR","ref:FR:FANTOIR:left","ref:FR:FANTOIR:right"]) AS fantoir,
        ST_Within(l.way,p.way)::integer as within,
        a9.nom AS nom_ac
FROM    (SELECT way FROM planet_osm_polygon WHERE "ref:INSEE" = '__code_insee__') p
JOIN    planet_osm_line l
ON      ST_Intersects(l.way, p.way)
LEFT OUTER JOIN (SELECT * FROM polygones_insee_a9 WHERE insee_a8 = '__code_insee__') a9
ON      ST_Intersects(l.way, a9.geometrie)
WHERE   (l.highway != '' OR
        l.waterway = 'dam')     AND
        l.highway != 'bus_stop' AND
        l.name != ''
UNION ALL
SELECT  ST_PointOnSurface(l.way),
        unnest(array[l.name,l.tags->'alt_name',l.tags->'old_name']) AS name,
        COALESCE(a9.code_insee,'xxxxx') as insee_jointure,
        a9.code_insee insee_ac,
        "ref:FR:FANTOIR" AS fantoir,
        ST_Within(l.way,p.geometrie)::integer as within,
        a9.nom AS nom_ac
FROM    (SELECT geometrie FROM polygones_insee WHERE code_insee = '__code_insee__') p
JOIN    planet_osm_polygon l
ON      ST_Intersects(l.way, p.geometrie)
LEFT OUTER JOIN (SELECT * FROM polygones_insee_a9 WHERE insee_a8 = '__code_insee__') a9
ON      ST_Intersects(l.way, a9.geometrie)
WHERE   (l.highway||"ref:FR:FANTOIR" != '' OR l.landuse = 'residential' OR l.amenity = 'parking') AND
        l.highway != 'bus_stop' AND
        l.name != ''
UNION ALL
SELECT l.way,
        unnest(array[l.name,l.tags->'alt_name',l.tags->'old_name']) AS name,
        COALESCE(a9.code_insee,'xxxxx') as insee_jointure,
        a9.code_insee insee_ac,
        "ref:FR:FANTOIR" AS fantoir,
        ST_Within(l.way,p.way)::integer as within,
        a9.nom AS nom_ac
FROM    (SELECT way FROM planet_osm_polygon WHERE "ref:INSEE" = '__code_insee__') p
JOIN    planet_osm_rels l
ON      ST_Intersects(l.way, p.way)
LEFT OUTER JOIN (SELECT * FROM polygones_insee_a9 WHERE insee_a8 = '__code_insee__') a9
ON      ST_Intersects(l.way, a9.geometrie)
WHERE   l.member_role = 'street' AND
        l.name != ''),
lignes_noms
AS
(SELECT CASE 
            WHEN GeometryType(way) = 'POINT' THEN ST_MakeLine(ST_Translate(way,-0.000001,-0.000001),ST_Translate(way,0.000001,0.000001))
            WHEN GeometryType(way) LIKE '%POLYGON' THEN ST_ExteriorRing(way)
            ELSE way
        END AS way_line,
        *
FROM    lignes_brutes
WHERE   name IS NOT NULL AND
        (fantoir LIKE '__code_insee__%' OR fantoir = '')),
lignes_noms_rang
AS
(SELECT *,
        RANK() OVER(PARTITION BY name,insee_ac ORDER BY within DESC, fantoir DESC) rang
FROM    lignes_noms),
lignes_agregees
AS
(SELECT ST_LineMerge(ST_Collect(way_line)) way,
        name,
        insee_ac,
        insee_jointure,
        fantoir,
        nom_ac
FROM    lignes_noms_rang
WHERE   rang = 1
GROUP BY 2,3,4,5,6),
centroide_lignes_agregees
AS
(SELECT ST_Centroid(ST_LineMerge(ST_Collect(way_line))) way,
        name,
        insee_ac,
        insee_jointure,
        fantoir,
        nom_ac
FROM    lignes_noms_rang
WHERE   rang = 1
GROUP BY 2,3,4,5,6),
resultat
AS
(SELECT ST_SetSRID(ST_ClosestPoint(lignes_agregees.way,centroide_lignes_agregees.way),4326) point,
        lignes_agregees.name,
        lignes_agregees.insee_ac,
        lignes_agregees.fantoir,
        lignes_agregees.nom_ac
FROM    lignes_agregees
JOIN    centroide_lignes_agregees
USING   (name,insee_jointure)),
complement
AS
(SELECT c.*,
        a9.code_insee AS insee_ac,
        a9.nom AS nom_ac
FROM    (SELECT pl.way point,
                pl.name,
                pl."ref:FR:FANTOIR" fantoir
        FROM    (SELECT way FROM planet_osm_polygon WHERE "ref:INSEE" = '__code_insee__') p
        JOIN    planet_osm_point    pl
        ON      pl.way && p.way                 AND
                ST_Intersects(pl.way, p.way)
        WHERE   (pl."ref:FR:FANTOIR" != ''  OR
                pl.junction != '') AND
                pl.highway != 'bus_stop' AND
                pl.name != ''
        UNION
        SELECT  ST_Centroid(pl.way),
                pl.name,
                pl."ref:FR:FANTOIR" f
        FROM    (SELECT way FROM planet_osm_polygon WHERE "ref:INSEE" = '__code_insee__') p
        JOIN    planet_osm_polygon  pl
        ON      pl.way && p.way                 AND
                ST_Intersects(pl.way, p.way)
        WHERE   (   pl.highway||pl."ref:FR:FANTOIR" != ''   OR
                    pl.landuse = 'residential' OR
                    pl.place = 'square' OR
                    pl.amenity = 'school')  AND
                    pl.highway != 'bus_stop' AND
                    pl.name != '')c
LEFT OUTER JOIN (SELECT * FROM polygones_insee_a9 WHERE insee_a8 = '__code_insee__') a9
ON      ST_Intersects(c.point, a9.geometrie))
SELECT  ST_x(point),
        ST_y(point),
        name,
        insee_ac,
        fantoir,
        nom_ac
FROM    resultat
UNION ALL
SELECT  ST_x(point),
        ST_y(point),
        name,
        insee_ac,
        fantoir,
        nom_ac
FROM    complement;
