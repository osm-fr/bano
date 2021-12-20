select 	ST_X(pt_geo),
		ST_Y(pt_geo),
		provenance,
		osm_id,
		hsnr,
		street_name,
		tags,
		''::text suffixe,
		insee_com
FROM 
-- point avec addr:street
		(SELECT	1 provenance,
				ST_Transform(pt.way,4326) pt_geo,
				pt.osm_id,
				pt."addr:housenumber" hsnr,
				pt."addr:street" street_name,
				null::hstore tags,
				p."ref:INSEE" insee_com
		 FROM	planet_osm_polygon	p
		 JOIN	planet_osm_point 	pt
		 ON		ST_Intersects(pt.way, p.way)
		 WHERE	p."ref:INSEE" = '__com__'	AND
				pt."addr:housenumber" != '' AND
				pt."addr:street" != ''
		UNION
-- way avec addr:street
		SELECT	2,
				ST_Transform(ST_Centroid(w.way),4326),
				w.osm_id,
				w."addr:housenumber",
				w."addr:street",
				null::hstore tags,
				p."ref:INSEE"
		 FROM	planet_osm_polygon	p
		 JOIN	planet_osm_polygon 	w
		 ON		ST_Intersects(w.way, p.way)
		 WHERE	p."ref:INSEE" = '__com__'	AND
				w."addr:housenumber" != '' AND
				w."addr:street" != ''
		UNION
-- point dans relation associatedStreet
		SELECT	3,
				ST_Transform(pt.way,4326),
				pt.osm_id,
				pt."addr:housenumber",
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
		UNION
-- way dans relation associatedStreet
		SELECT	4,
				ST_Transform(ST_Centroid(w.way),4326),
				w.osm_id,
				w."addr:housenumber",
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
)a;

