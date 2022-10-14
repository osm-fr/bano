SELECT  DISTINCT provenance,
        name,
        tags,
        libelle_suffixe,
        a9.code_insee,
        a9.nom,
        nature
FROM    (SELECT  1::integer AS provenance,
                 pt.way,
                 UNNEST(ARRAY[pt.name,pt.tags->'alt_name',pt.tags->'old_name']) as name,
                 tags,
                 CASE
                     WHEN pt.place='' THEN 'voie'::text
                     ELSE 'place'
                 END AS nature
         FROM    (SELECT way FROM planet_osm_polygon WHERE "ref:INSEE" = '__code_insee__')                    p
         JOIN    (SELECT * FROM planet_osm_point WHERE ("ref:FR:FANTOIR" !='' OR place != '') AND name != '') pt
         ON      pt.way && p.way                 AND
                 ST_Intersects(pt.way, p.way)
         UNION ALL
         SELECT  2,
                 l.way,
                 UNNEST(ARRAY[l.name,l.tags->'alt_name',l.tags->'old_name']) as name,
                 tags,
                 'voie'
         FROM    (SELECT way FROM planet_osm_polygon WHERE "ref:INSEE" = '__code_insee__') p
         JOIN    (SELECT * FROM planet_osm_line WHERE highway != '' AND name != '')        l
         ON      p.way && l.way AND ST_Contains(p.way, l.way)
         UNION ALL
         SELECT  3,
                 pl.way,
                 UNNEST(ARRAY[pl.name,pl.tags->'alt_name',pl.tags->'old_name']) as name,
                 tags,
                 'voie'
         FROM    (SELECT way FROM planet_osm_polygon WHERE "ref:INSEE" = '__code_insee__')                                                                    p
         JOIN    (SELECT * FROM planet_osm_polygon WHERE (highway||"ref:FR:FANTOIR" != '' OR landuse = 'residential' OR amenity = 'parking') AND name != '') pl
         ON      pl.way && p.way                 AND
                 ST_Intersects(pl.way, p.way)) l
LEFT OUTER JOIN suffixe h
ON      ST_Intersects(l.way, h.geometrie)
LEFT OUTER JOIN (SELECT * FROM polygones_insee_a9 where insee_a8 = '__code_insee__') a9
ON      ST_Contains(a9.geometrie,way)
WHERE   l.name IS NOT NULL;