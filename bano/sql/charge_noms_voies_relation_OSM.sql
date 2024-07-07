SELECT  DISTINCT provenance,
        name,
        name_tag,
        tags,
        libelle_suffixe,
        a9.code_insee,
        a9.nom,
        'voie'::text
FROM    (SELECT 4::integer AS provenance,
                name_osm.name,
                name_osm.name_tag,
                l.way,
                r.tags
         FROM   (SELECT way FROM planet_osm_polygon WHERE "ref:INSEE" = '__code_insee__')    p
         JOIN   (SELECT name,alt_name,old_name,tags,osm_id,way FROM planet_osm_line WHERE highway != '' AND name != '') l
         ON     p.way && l.way AND ST_Contains(p.way, l.way)
         JOIN   planet_osm_rels r
         ON     r.osm_id = l.osm_id,
         UNNEST(
             ARRAY [l.name,l.alt_name,l.old_name],
             ARRAY ['name','alt_name','old_name']
         ) AS name_osm(name,name_tag)
         UNION ALL
         SELECT 5,
                name_osm.name,
                name_osm.name_tag,
                l.way,
                r.tags
         FROM   (SELECT way FROM planet_osm_polygon WHERE "ref:INSEE" = '__code_insee__')    p
         JOIN   (SELECT name,alt_name,old_name,tags,osm_id,way FROM planet_osm_polygon WHERE highway != '' AND name != '') l
         ON     p.way && l.way AND ST_Contains(p.way, l.way)
         JOIN   planet_osm_rels r
         ON     r.osm_id = l.osm_id,
         UNNEST(
                ARRAY [l.name,l.alt_name,l.old_name],
                ARRAY ['name','alt_name','old_name']
         ) AS name_osm(name,name_tag)
) l
LEFT OUTER JOIN (SELECT * FROM suffixe WHERE code_insee = '__code_insee__') h
ON            ST_Intersects(way, h.geometrie)
LEFT OUTER JOIN (SELECT * FROM polygones_insee_a9 where insee_a8 = '__code_insee__') a9
ON            ST_Contains(a9.geometrie,way)
WHERE l.name IS NOT NULL;
