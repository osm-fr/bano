SELECT  DISTINCT provenance,
        name,
        tags,
        libelle_suffixe,
        a9.code_insee,
        a9.nom,
        'voie'::text
FROM    (SELECT 4::integer AS provenance,
                UNNEST(ARRAY[l.name,l.alt_name,l.old_name,l.name_fr,l.name_eu,l.name_br,l.name_oc,l.name_de,l.name_ca,l.name_gsw,l.name_co]) as name,
                l.way,
                r.tags
         FROM   (SELECT way FROM planet_osm_polygon WHERE "ref:INSEE" = '__code_insee__')    p
         JOIN   (SELECT name,alt_name,old_name,name_fr,name_eu,name_br,name_oc,name_de,name_ca,name_gsw,name_co,tags,osm_id,way FROM planet_osm_line WHERE highway != '' AND name != '') l
         ON     p.way && l.way AND ST_Contains(p.way, l.way)
         JOIN   planet_osm_rels r
         ON     r.osm_id = l.osm_id
         UNION ALL
         SELECT 5,
                UNNEST(ARRAY[l.name,l.alt_name,l.old_name,l.name_fr,l.name_eu,l.name_br,l.name_oc,l.name_de,l.name_ca,l.name_gsw,l.name_co]) as name,
                l.way,
                r.tags
         FROM   (SELECT way FROM planet_osm_polygon WHERE "ref:INSEE" = '__code_insee__')    p
         JOIN   (SELECT name,alt_name,old_name,name_fr,name_eu,name_br,name_oc,name_de,name_ca,name_gsw,name_co,tags,osm_id,way FROM planet_osm_polygon WHERE highway != '' AND name != '') l
         ON     p.way && l.way AND ST_Contains(p.way, l.way)
         JOIN   planet_osm_rels r
         ON     r.osm_id = l.osm_id) l
LEFT OUTER JOIN (SELECT * FROM suffixe WHERE code_insee = '__code_insee__') h
ON            ST_Intersects(way, h.geometrie)
LEFT OUTER JOIN (SELECT * FROM polygones_insee_a9 where insee_a8 = '__code_insee__') a9
ON            ST_Contains(a9.geometrie,way)
WHERE l.name IS NOT NULL;
