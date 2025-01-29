select 	ST_X(way),
		ST_Y(way),
		provenance,
		hsnr,
		street_name,
		null::text place_name,
		tags,
		h.libelle_suffixe,
		code_postal,
		code_insee_a9,
		nom_a9
FROM 
-- point dans relation associatedStreet
		(SELECT	5 provenance,
				pt.way,
				pt."addr:housenumber" hsnr,
				null::text street_name,
				r.tags tags,
				pt."addr:postcode"    AS code_postal
		FROM	(SELECT ST_SetSRID(ST_Extent(geometrie),4326) way, code_insee FROM polygones_insee WHERE code_insee = '__code_insee__'  GROUP BY 2) p
		JOIN	planet_osm_point 	pt
		ON		ST_Intersects(pt.way,p.way)
		JOIN	planet_osm_rels 	r
		ON		r.osm_id = pt.osm_id
		WHERE	pt."addr:housenumber" != ''
		UNION
-- way dans relation associatedStreet
		SELECT	6,
				ST_PointOnSurface(w.way),
				w."addr:housenumber",
				null,
				r.tags,
				w."addr:postcode"
		FROM	(SELECT ST_SetSRID(ST_Extent(geometrie),4326) way, code_insee FROM polygones_insee WHERE code_insee = '__code_insee__'  GROUP BY 2) p
		JOIN	planet_osm_polygon 	w
		ON		ST_Intersects(w.way, p.way)
		JOIN	planet_osm_rels 	r
		ON		r.osm_id = w.osm_id
		WHERE	w."addr:housenumber" != '')a
LEFT OUTER JOIN (SELECT * FROM suffixe WHERE code_insee = '__code_insee__') h
ON		ST_Intersects(a.way, h.geometrie)
LEFT OUTER JOIN (SELECT geometrie, code_insee code_insee_a9,nom nom_a9 FROM polygones_insee_a9 WHERE insee_a8 = '__code_insee__') a9
ON		ST_Intersects(a.way, a9.geometrie);


 