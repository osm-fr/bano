SELECT	pl.name,
		pl.tags->'ref:FR:FANTOIR' f,
		'' fl,
		'' fr,
		h.suffixe,
		p.tags->'ref:INSEE'
FROM	planet_osm_polygon 	p
JOIN	planet_osm_point 	pl
ON		pl.way && p.way					AND
		ST_Intersects(pl.way, p.way)
LEFT OUTER JOIN (__suffixe_data__) h
ON		ST_Intersects(pl.way, h.geom)
WHERE	p.tags ? 'ref:INSEE'			AND
		p.tags->'ref:INSEE'='__com__'	AND
		pl.tags->'ref:FR:FANTOIR'!=''			AND
		pl.name 	IS NOT NULL
--		group by 1,2,3,4
UNION
SELECT	l.name,
		l.tags->'ref:FR:FANTOIR' f,
		l.tags->'ref:FR:FANTOIR:left' fl,
		l.tags->'ref:FR:FANTOIR:right' fr,
		h.suffixe,
		p.tags->'ref:INSEE'
FROM	planet_osm_polygon 	p
JOIN	planet_osm_line 	l
ON		ST_Intersects(l.way, p.way)
LEFT OUTER JOIN (__suffixe_data__) h
ON		ST_Intersects(l.way, h.geom)
WHERE	p.tags ? 'ref:INSEE'			AND
		p.tags->'ref:INSEE'='__com__'	AND
		l.highway 	IS NOT NULL			AND
		l.name 		IS NOT NULL
	--	group by 1,2,3,4,5
UNION
SELECT	pl.name,
		pl.tags->'ref:FR:FANTOIR' f,
		pl.tags->'ref:FR:FANTOIR:left' fl,
		pl.tags->'ref:FR:FANTOIR:right' fr,
		h.suffixe,
		p.tags->'ref:INSEE'
FROM	planet_osm_polygon 	p
JOIN	planet_osm_polygon 	pl
ON		pl.way && p.way					AND
		ST_Intersects(pl.way, p.way)
LEFT OUTER JOIN (__suffixe_data__) h
ON		ST_Intersects(pl.way, h.geom)
WHERE	p.tags ? 'ref:INSEE'				AND
		p.tags->'ref:INSEE'='__com__'		AND
	--	pl.highway 	IS NOT NULL				AND
		(	coalesce(pl.highway,pl.tags->'ref:FR:FANTOIR') 	IS NOT NULL	OR
					pl.landuse = 'residential'							OR
					pl.amenity = 'parking')	AND
		pl.name 	IS NOT NULL
	--	group by 1,2,3,4,5
		;
