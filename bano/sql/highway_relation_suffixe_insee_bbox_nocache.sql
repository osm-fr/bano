SELECT	DISTINCT l.name,
		r.tags,
		h.libelle_suffixe,
		p."ref:INSEE"
FROM	planet_osm_polygon 	p
JOIN	planet_osm_line 	l
ON		l.way && p.way
JOIN	planet_osm_rels		r
ON		r.osm_id = l.osm_id
LEFT OUTER JOIN suffixe h
ON		ST_Intersects(l.way, h.geometrie)
WHERE	p."ref:INSEE" = '__com__' AND
		l.highway != '' AND
		l.name != ''
UNION ALL
SELECT	DISTINCT l.name,
		r.tags,
		h.libelle_suffixe,
		p."ref:INSEE"
FROM	planet_osm_polygon 	p
JOIN	planet_osm_polygon 	l
ON		l.way && p.way
JOIN	planet_osm_rels		r
ON		r.osm_id = l.osm_id
LEFT OUTER JOIN suffixe h
ON		ST_Intersects(l.way, h.geometrie)
WHERE	p."ref:INSEE" = '__com__' AND
		l.highway != '' AND
		l.name != '';
				
