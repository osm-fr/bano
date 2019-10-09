SELECT ST_X(geometrie),
       ST_Y(geometrie),
       nom,
       fantoir,
       insee_com
FROM   cadastre_2_place
WHERE  insee_com = '__com__';