SELECT	DISTINCT l.name,
		r.tags,
		h.libelle_suffixe,
		'__code_insee__',
		a9.insee_com,
		a9.nom,
		'voie'::text
FROM	(SELECT way FROM planet_osm_polygon WHERE "ref:INSEE" = '__code_insee__')	p
JOIN	(SELECT name,osm_id,way FROM planet_osm_line WHERE highway != '' AND name != '') l
ON		l.way && p.way
JOIN	planet_osm_rels		r
ON		r.osm_id = l.osm_id
LEFT OUTER JOIN suffixe h
ON		ST_Intersects(l.way, h.geometrie)
LEFT OUTER JOIN (SELECT * FROM polygones_insee_a9 where insee_a8 = '__code_insee__') a9
ON		ST_Contains(a9.geometrie,l.way)
UNION ALL
SELECT	DISTINCT l.name,
		r.tags,
		h.libelle_suffixe,
		'__code_insee__',
		a9.insee_com,
		a9.nom,
		'voie'::text
FROM	(SELECT way FROM planet_osm_polygon WHERE "ref:INSEE" = '__code_insee__')	p
JOIN	(SELECT name,osm_id,way FROM planet_osm_polygon WHERE highway != '' AND name != '') l
ON		l.way && p.way
JOIN	planet_osm_rels		r
ON		r.osm_id = l.osm_id
LEFT OUTER JOIN suffixe h
ON		ST_Intersects(l.way, h.geometrie)
LEFT OUTER JOIN (SELECT * FROM polygones_insee_a9 where insee_a8 = '__code_insee__') a9
ON		ST_Contains(a9.geometrie,l.way);
				
