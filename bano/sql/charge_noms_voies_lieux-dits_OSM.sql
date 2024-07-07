SELECT  DISTINCT provenance,
        name,
        name_tag,
        tags,
        libelle_suffixe,
        a9.code_insee,
        a9.nom,
        nature
FROM    (SELECT  1::integer AS provenance,
                 pt.way,
                 name_osm.name,
                 name_osm.name_tag,
                 tags,
                 CASE
                     WHEN pt.place='' THEN 'voie'::text
                     ELSE 'place'
                 END AS nature
         FROM    (SELECT way FROM planet_osm_polygon WHERE "ref:INSEE" = '__code_insee__')                    p
         JOIN    (SELECT * FROM planet_osm_point WHERE ("ref:FR:FANTOIR" !='' OR place != '') AND name != '') pt
         ON      pt.way && p.way                 AND
                 ST_Intersects(pt.way, p.way),
         UNNEST(
             ARRAY [pt.name,pt.alt_name,pt.old_name],
             ARRAY ['name','alt_name','old_name']
         ) AS name_osm(name,name_tag)
         UNION ALL
         SELECT  2,
                 l.way,
                 name_osm.name,
                 name_osm.name_tag,
                 tags,
                 'voie'
         FROM    (SELECT way FROM planet_osm_polygon WHERE "ref:INSEE" = '__code_insee__') p
         JOIN    (SELECT * FROM planet_osm_line WHERE highway != '' AND name != '')        l
         ON      p.way && l.way AND ST_Contains(p.way, l.way),
         UNNEST(
             ARRAY [l.name,l.alt_name,l.old_name],
             ARRAY ['name','alt_name','old_name']
         ) AS name_osm(name,name_tag)
         UNION ALL
         SELECT  3,
                 pl.way,
                 name_osm.name,
                 name_osm.name_tag,
                 tags,
                 'voie'
         FROM    (SELECT way FROM planet_osm_polygon WHERE "ref:INSEE" = '__code_insee__')                                                                    p
         JOIN    (SELECT * FROM planet_osm_polygon WHERE (highway||"ref:FR:FANTOIR" != '' OR landuse = 'residential' OR amenity = 'parking') AND name != '') pl
         ON      pl.way && p.way                 AND
                 ST_Intersects(pl.way, p.way),
         UNNEST(
             ARRAY [pl.name,pl.alt_name,pl.old_name],
             ARRAY ['name','alt_name','old_name']
         ) AS name_osm(name,name_tag)
) l
LEFT OUTER JOIN suffixe h
ON      ST_Intersects(l.way, h.geometrie)
LEFT OUTER JOIN (SELECT * FROM polygones_insee_a9 where insee_a8 = '__code_insee__') a9
ON      ST_Contains(a9.geometrie,way)
WHERE   l.name IS NOT NULL;
