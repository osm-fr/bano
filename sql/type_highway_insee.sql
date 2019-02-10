SELECT  pl.name,
        pl.highway,
        p."ref:INSEE"
FROM    planet_osm_polygon     p
JOIN    planet_osm_point     pl
        ON      pl.way && p.way                    AND
                ST_Intersects(pl.way, p.way)
        WHERE   p."ref:INSEE" = '__com__'    AND
                pl.highway     != ''   AND
                pl.name     != ''
UNION
SELECT  l.name,
        l.highway,
        p."ref:INSEE"
        FROM    planet_osm_polygon     p
        JOIN    planet_osm_line     l
        ON      ST_Intersects(l.way, p.way)
        WHERE   p."ref:INSEE" = '__com__'    AND
                l.highway     != ''           AND
                l.name        != ''
UNION
SELECT  pl.name,
        pl.highway,
        p."ref:INSEE"
        FROM    planet_osm_polygon     p
        JOIN    planet_osm_polygon     pl
        ON      pl.way && p.way                    AND
                ST_Intersects(pl.way, p.way)
        WHERE   p."ref:INSEE" = '__com__'    AND
                pl.highway     != ''            AND
                pl.name     != ''
ORDER BY 1;
