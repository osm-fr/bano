SELECT	DISTINCT l.name,r.tags,p.tags->'ref:INSEE'
FROM	planet_osm_polygon 	p
JOIN	planet_osm_line 	l
ON	ST_Intersects(l.way, p.way)
JOIN	planet_osm_rels		r
ON	r.parts @> ARRAY[l.osm_id]
WHERE	p.tags ? 'ref:INSEE'		AND
	p.tags->'ref:INSEE'='__com__'	AND
	l.highway 	IS NOT NULL	AND
	l.name 		IS NOT NULL AND
    r.tags IS NOT NULL
ORDER BY 3;
				
