WITH
pts
AS
(SELECT  pt.way,
        UNNEST(ARRAY[pt.name,pt.tags->'alt_name',pt.tags->'old_name']) as name,
        tags,
        place,
        a9.code_insee AS insee_ac,
        "ref:FR:FANTOIR" AS fantoir,
        a9.nom AS nom_ac 
FROM    (SELECT way FROM planet_osm_polygon WHERE "ref:INSEE" = '__code_insee__')                    p
JOIN    (SELECT * FROM planet_osm_point WHERE place != '' AND name != '') pt
ON      pt.way && p.way                 AND
         ST_Intersects(pt.way, p.way)
LEFT OUTER JOIN (SELECT * FROM polygones_insee_a9 WHERE insee_a8 = '__code_insee__') a9
ON      ST_Intersects(pt.way, a9.geometrie))
SELECT  ST_x(way),
        ST_y(way),
        name,
        insee_ac,
        fantoir,
        nom_ac
FROM    pts
WHERE   name IS NOT NULL;