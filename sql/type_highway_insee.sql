SELECT	pl.name,pl.highway,p.tags->'ref:INSEE'
		FROM	planet_osm_polygon 	p
		JOIN	planet_osm_point 	pl
		ON		pl.way && p.way					AND
				ST_Intersects(pl.way, p.way)
		WHERE	p.tags ? 'ref:INSEE'			AND
				p.tags->'ref:INSEE'='__com__'	AND
				pl.highway 	IS NOT NULL	AND
				pl.name 	IS NOT NULL
UNION
SELECT	l.name,l.highway,p.tags->'ref:INSEE'
		FROM	planet_osm_polygon 	p
		JOIN	planet_osm_line 	l
		ON		ST_Intersects(l.way, p.way)
		WHERE	p.tags ? 'ref:INSEE'			AND
				p.tags->'ref:INSEE'='__com__'	AND
				l.highway 	IS NOT NULL			AND
				l.name 		IS NOT NULL
UNION
SELECT	pl.name,pl.highway,p.tags->'ref:INSEE'
		FROM	planet_osm_polygon 	p
		JOIN	planet_osm_polygon 	pl
		ON		pl.way && p.way					AND
				ST_Intersects(pl.way, p.way)
		WHERE	p.tags ? 'ref:INSEE'			AND
				p.tags->'ref:INSEE'='__com__'	AND
				pl.highway 	IS NOT NULL			AND
				pl.name 	IS NOT NULL
ORDER BY 1;