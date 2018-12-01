select 	ST_X(pt_geo)::character varying,
		ST_Y(pt_geo)::character varying,
		provenance::character varying,
		osm_id::character varying,
		hsnr,
		street_name,
		tags,
		''::text suffixe,
		insee_com
FROM 
-- point dans relation associatedStreet
		(SELECT	3 provenance,
				ST_Transform(pt.way,4326) pt_geo,
				pt.osm_id::character varying,
				pt."addr:housenumber" hsnr,
				null street_name,
				r.tags,
				p.tags->'ref:INSEE' insee_com
		FROM	planet_osm_polygon	p
		JOIN	planet_osm_point 	pt
		ON		pt.way && p.way
		JOIN	planet_osm_rels 	r
		ON		r.parts @> ARRAY[pt.osm_id]
		WHERE	p.tags ? 'ref:INSEE'				AND
				p.tags->'ref:INSEE'='__com__'		AND
				pt."addr:housenumber"	IS NOT NULL     AND
				r.tags IS NOT NULL
		UNION
-- way dans relation associatedStreet
		SELECT	4,
				ST_Transform(ST_Centroid(w.way),4326),
				w.osm_id::character varying,
				w."addr:housenumber",
				null,
				r.tags,
				p.tags->'ref:INSEE'
		FROM	planet_osm_polygon	p
		JOIN	planet_osm_polygon 	w
		ON		w.way && p.way
		JOIN	planet_osm_rels 	r
		ON		r.parts @> ARRAY[w.osm_id]
		WHERE	p.tags ? 'ref:INSEE'				AND
				p.tags->'ref:INSEE'='__com__'		AND
				w."addr:housenumber"	IS NOT NULL     AND
				r.tags IS NOT NULL
		
)a
ORDER BY 9
-- where hsnr is not null*/		
;

