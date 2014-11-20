SELECT	DISTINCT l.name,
		l.tags->'ref:FR:FANTOIR' f,
		l.tags->'ref:FR:FANTOIR:left' fl,
		l.tags->'ref:FR:FANTOIR:right' fr,
		'' suffixe,
		p.tags->'ref:INSEE'
FROM	planet_osm_polygon 	p
JOIN	planet_osm_line 	l
ON		l.way && p.way
WHERE	p.tags ? 'ref:INSEE'			AND
		p.tags->'ref:INSEE'='__com__'	AND
		l.highway 	IS NOT NULL	AND
		l.name 		IS NOT NULL
ORDER BY 6;
