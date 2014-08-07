select 	ST_X(a.pt_geo)::character varying,
		ST_Y(a.pt_geo)::character varying,
		a.provenance::character varying,
		a.osm_id::character varying,
		a.hsnr,
		a.street_name,
		a.tags,
		h.suffixe
FROM 
-- point avec addr:street
		(SELECT	1 provenance,
				ST_Transform(pt.way,4326) pt_geo,
				pt.osm_id::character varying,
				pt."addr:housenumber" hsnr,
				pt.tags->'addr:street' street_name,
				ARRAY[]::character[] tags
		 FROM	planet_osm_polygon	p
		 JOIN	planet_osm_point 	pt
		 ON		ST_Intersects(pt.way, p.way)
		 WHERE	p.tags ? 'ref:INSEE'			AND
				p.tags->'ref:INSEE'='__com__'	AND
				pt."addr:housenumber"	IS NOT NULL AND
				pt.tags->'addr:street'!=''
		UNION
-- way avec addr:street
		SELECT	2,
				ST_Transform(ST_Centroid(w.way),4326),
				w.osm_id::character varying,
				w."addr:housenumber",
				w.tags->'addr:street',
				ARRAY[]::character[]
		 FROM	planet_osm_polygon	p
		 JOIN	planet_osm_polygon 	w
		 ON		ST_Intersects(w.way, p.way)
		 WHERE	p.tags ? 'ref:INSEE'			AND
				p.tags->'ref:INSEE'='__com__'	AND
				-- w."addr:housenumber"	!='' AND
				w."addr:housenumber"	IS NOT NULL AND
				w.tags->'addr:street'!=''
		UNION
-- point dans relation associatedStreet
		SELECT	3,
				ST_Transform(pt.way,4326),
				pt.osm_id::character varying,
				pt."addr:housenumber",
				null,
				r.tags
		FROM	planet_osm_polygon	p
		JOIN	planet_osm_point 	pt
		ON		ST_Intersects(pt.way, p.way)
		JOIN	planet_osm_rels 	r
		ON		r.parts @> ARRAY[pt.osm_id]
		WHERE	p.tags ? 'ref:INSEE'				AND
				p.tags->'ref:INSEE'='__com__'		AND
				pt."addr:housenumber"	IS NOT NULL
		UNION
-- way dans relation associatedStreet
		SELECT	4,
				ST_Transform(ST_Centroid(w.way),4326),
				w.osm_id::character varying,
				w."addr:housenumber",
				null,
				r.tags
		FROM	planet_osm_polygon	p
		JOIN	planet_osm_polygon 	w
		ON		ST_Intersects(w.way, p.way)
		JOIN	planet_osm_rels 	r
		ON		r.parts @> ARRAY[w.osm_id]
		WHERE	p.tags ? 'ref:INSEE'				AND
				p.tags->'ref:INSEE'='__com__'		AND
				w."addr:housenumber"	IS NOT NULL
		
)a
LEFT OUTER JOIN (__suffixe_data__) h
ON		ST_Intersects(a.pt_geo, ST_Transform(h.geom,4326));

