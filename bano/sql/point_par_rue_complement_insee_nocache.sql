SELECT 	ST_X(ST_Transform(ST_SetSRID(way,3857),4326)),
		ST_Y(ST_Transform(ST_SetSRID(way,3857),4326)),
		name,
		fantoir,
		suffixe,
		insee
FROM	(SELECT	pl.way,
				pl.name,
				pl."ref:FR:FANTOIR" fantoir,
				'' suffixe,
				p."ref:INSEE" insee
		FROM	planet_osm_polygon 	p
		JOIN	planet_osm_point 	pl
		ON		pl.way && p.way					AND
				ST_Intersects(pl.way, p.way)
		WHERE	p."ref:INSEE" = '__com__'	AND
				pl."ref:FR:FANTOIR" != ''	AND
				pl.name != ''
		UNION
		SELECT	ST_Centroid(pl.way),
				pl.name,
				pl."ref:FR:FANTOIR" f,
				'' suffixe,
				p."ref:INSEE"
		FROM	planet_osm_polygon 	p
		JOIN	planet_osm_polygon 	pl
		ON		pl.way && p.way					AND
				ST_Intersects(pl.way, p.way)
		WHERE	p."ref:INSEE" = '__com__'	AND
				(	pl.highway||pl."ref:FR:FANTOIR" != ''	OR
					pl.landuse = 'residential' OR
					pl.place = 'square' OR
					pl.amenity = 'school')	AND
				pl.name != '')a;