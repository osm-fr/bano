select 	ST_X(pt_way),
		ST_Y(pt_way),
		provenance,
		hsnr,
		street_name,
		tags,
		h.libelle_suffixe,
		insee_com
FROM 
-- point avec addr:street
		(SELECT	1 provenance,
				pt.way,
				pt."addr:housenumber" hsnr,
				pt."addr:street" street_name,
				pt."addr:place"  place_name,
				null::hstore tags,
				p."ref:INSEE" insee_com
		 FROM	planet_osm_polygon	p
		 JOIN	planet_osm_point 	pt
		 ON		ST_Intersects(pt.way, p.way)
		 WHERE	p."ref:INSEE" = '__com__'	AND
				pt."addr:housenumber" != '' AND
				pt."addr:street" != ''
		UNION ALL
-- way avec addr:street
		SELECT	2,
				ST_Centroid(w.way),
				w."addr:housenumber",
				w."addr:street",
				pt."addr:place",
				null::hstore tags,
				p."ref:INSEE"
		 FROM	planet_osm_polygon	p
		 JOIN	planet_osm_polygon 	w
		 ON		ST_Intersects(w.way, p.way)
		 WHERE	p."ref:INSEE" = '__com__'	AND
				w."addr:housenumber" != '' AND
				w."addr:street" != ''
		UNION ALL
-- point dans relation associatedStreet
		SELECT	3,
				pt.way,
				pt."addr:housenumber",
				null,
				null,
				r.tags,
				p."ref:INSEE"
		FROM	planet_osm_polygon	p
		JOIN	planet_osm_point 	pt
		ON		ST_Intersects(pt.way, p.way)
		JOIN	planet_osm_rels 	r
		ON		r.osm_id = pt.osm_id
		WHERE	p."ref:INSEE" = '__com__' AND
				pt."addr:housenumber" != ''
		UNION ALL
-- way dans relation associatedStreet
		SELECT	4,
				ST_Centroid(w.way),
				w."addr:housenumber",
				null,
				null,
				r.tags,
				p."ref:INSEE"
		FROM	planet_osm_polygon	p
		JOIN	planet_osm_polygon 	w
		ON		ST_Intersects(w.way, p.way)
		JOIN	planet_osm_rels 	r
		ON		r.osm_id = w.osm_id
		WHERE	p."ref:INSEE" = '__com__' AND
				w."addr:housenumber" != ''
)a
LEFT OUTER JOIN suffixe h
ON		ST_Intersects(a.way, h.geometrie);
