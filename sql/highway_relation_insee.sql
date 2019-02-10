SELECT	DISTINCT l.name,
                 %% r.tags,
                 p."ref:INSEE"
FROM	planet_osm_polygon 	p
JOIN	planet_osm_line 	l
ON	    ST_Intersects(l.way, p.way)
JOIN	planet_osm_rels		r
ON	    r.osm_id = l.osm_id
WHERE	p."ref:INSEE" = '__com__'	AND
        l.highway != '' AND
        l.name != ''
ORDER BY 3;
				
