select 	ST_X(ST_Transform(a.pt_geo,4326))::character varying,
		ST_Y(ST_Transform(a.pt_geo,4326))::character varying,
		a.provenance::character varying,
		a.osm_id::character varying,
		a.hsnr,
		a.street_name,
		a.tags,
		h.libelle_suffixe,
		a.insee_com
FROM 
-- point avec addr:street
		(SELECT	1 provenance,
				pt.way pt_geo,
				pt.osm_id::character varying,
				pt."addr:housenumber" hsnr,
				pt."addr:street" street_name,
				ARRAY[]::character[] tags,
				p."ref:INSEE" insee_com
		 FROM	planet_osm_polygon	p
		 JOIN	planet_osm_point 	pt
		 ON		ST_Intersects(pt.way, p.way)
		 WHERE	p."ref:INSEE" = '__com__'	AND
				pt."addr:housenumber" != ''AND
				pt."addr:street" !=''
		UNION
-- way avec addr:street
		SELECT	2,
				ST_Centroid(w.way),
				w.osm_id::character varying,
				w."addr:housenumber",
				w."addr:street",
				ARRAY[]::character[],
				p."ref:INSEE"
		 FROM	planet_osm_polygon	p
		 JOIN	planet_osm_polygon 	w
		 ON		ST_Intersects(w.way, p.way)
		 WHERE	p."ref:INSEE" = '__com__'	AND
				w."addr:housenumber"	!='' AND
				w.tags->'addr:street' != ''
		UNION
-- point dans relation associatedStreet
		SELECT	3,
				pt.way,
				pt.osm_id::character varying,
				pt."addr:housenumber",
				null,
				r.tags,
				p."ref:INSEE"
		FROM	planet_osm_polygon	p
		JOIN	planet_osm_point 	pt
		ON		ST_Intersects(pt.way, p.way)
		JOIN	planet_osm_rels 	r
		ON		r.osm_id = pt.osm_id
		WHERE	p."ref:INSEE" = '__com__'		AND
				pt."addr:housenumber"	!= ''
		UNION
-- way dans relation associatedStreet
		SELECT	4,
				ST_Centroid(w.way),
				w.osm_id::character varying,
				w."addr:housenumber",
				null,
				r.tags,
				p."ref:INSEE"
		FROM	planet_osm_polygon	p
		JOIN	planet_osm_polygon 	w
		ON		ST_Intersects(w.way, p.way)
		JOIN	planet_osm_rels 	r
		ON		r.osm_id = w.osm_id
		WHERE	p."ref:INSEE" = '__com__'		AND
				w."addr:housenumber" != ''
		
)a
LEFT OUTER JOIN suffixe h
ON		ST_Intersects(a.pt_geo, h.geometrie);

