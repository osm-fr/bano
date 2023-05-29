SELECT  ST_X(geom_centroid),
        ST_Y(geom_centroid),
        regexp_replace(regexp_replace(regexp_replace(regexp_replace(ld.nom,'     ',' ','g'),'    ',' ','g'),'   ',' ','g'),'  ',' ','g') AS nom,
        a9.code_insee,
        a9.nom
FROM    (SELECT *
         FROM   lieux_dits
         WHERE  code_insee = '__code_insee__' AND
                nom IS NOT NULL) ld
LEFT OUTER JOIN suffixe h
ON      ST_Intersects(ld.geom_centroid, h.geometrie)
LEFT OUTER JOIN (SELECT * FROM polygones_insee_a9 WHERE insee_a8 = '__code_insee__') a9
ON      ST_Contains(a9.geometrie,ld.geom_centroid);