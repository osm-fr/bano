SELECT 	ST_X(way),
		ST_Y(way),
		provenance,
		hsnr,
		street_name,
		place_name,
		tags,
		h.libelle_suffixe,
		code_postal,
		code_insee_a9,
		nom_a9
FROM 
-- point avec addr:street ou addr:place
		(SELECT	1 provenance,
				pt.way,
				pt."addr:housenumber" AS hsnr,
				pt."addr:street"      AS street_name,
				pt."addr:place"       AS place_name,
				tags,
				pt."addr:postcode"    AS code_postal
		FROM	(SELECT geometrie FROM polygones_insee WHERE admin_level = 8 AND code_insee = '__code_insee__') p
		JOIN	planet_osm_point 	pt
		ON		ST_Intersects(pt.way, p.geometrie)
		WHERE	pt."addr:housenumber" != ''  AND
				pt."addr:street"||pt."addr:place" != ''
		UNION ALL
-- way avec addr:street ou addr:place
		SELECT	2,
				ST_PointOnSurface(w.way),
				w."addr:housenumber",
				w."addr:street",
				w."addr:place",
				tags,
				w."addr:postcode"
		FROM	(SELECT geometrie FROM polygones_insee WHERE admin_level = 8 AND code_insee = '__code_insee__') p
		JOIN	planet_osm_polygon 	w
		ON		ST_Intersects(w.way, p.geometrie)
		WHERE	w."addr:housenumber" != ''   AND
				w."addr:street"||w."addr:place" != ''
		UNION ALL
-- point dans relation associatedStreet
		SELECT	3,
				pt.way,
				pt."addr:housenumber",
				null,
				null,
				r.tags,
				pt."addr:postcode"
		FROM	(SELECT geometrie FROM polygones_insee WHERE admin_level = 8 AND code_insee = '__code_insee__') p
	    JOIN	planet_osm_point 	pt
		ON		ST_Intersects(pt.way, p.geometrie)
		JOIN	planet_osm_rels 	r
		ON		r.osm_id = pt.osm_id
		WHERE	pt."addr:housenumber" != ''
		UNION ALL
-- way dans relation associatedStreet
		SELECT	4,
				ST_PointOnSurface(w.way),
				w."addr:housenumber",
				null,
				null,
				r.tags,
				w."addr:postcode"
		FROM	(SELECT geometrie FROM polygones_insee WHERE admin_level = 8 AND code_insee = '__code_insee__') p
		JOIN	planet_osm_polygon 	w
		ON		ST_Intersects(w.way, p.geometrie)
		JOIN	planet_osm_rels 	r
		ON		r.osm_id = w.osm_id
		WHERE	w."addr:housenumber" != ''
		UNION ALL
-- relation multipoly dans relation associatedStreet
		SELECT	4,
				ST_PointOnSurface(w.way),
				w."addr:housenumber",
				null,
				null,
				r.tags,
				w."addr:postcode"
		FROM	(SELECT geometrie FROM polygones_insee WHERE admin_level = 8 AND code_insee = '__code_insee__') p
		JOIN	planet_osm_polygon 	w
		ON		ST_Intersects(w.way, p.geometrie)
		JOIN	(SELECT * FROM planet_osm_rels WHERE osm_type = 2)	r
		ON		-r.osm_id = w.osm_id
		WHERE	w."addr:housenumber" != ''
)a
LEFT OUTER JOIN (SELECT * FROM suffixe WHERE code_insee = '__code_insee__') h
ON		ST_Intersects(a.way, h.geometrie)
LEFT OUTER JOIN (SELECT geometrie, code_insee code_insee_a9,nom nom_a9 FROM polygones_insee_a9 WHERE insee_a8 = '__code_insee__') a9
ON		ST_Intersects(a.way, a9.geometrie);
