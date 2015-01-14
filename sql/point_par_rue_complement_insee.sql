SELECT 	ST_X(way),
		ST_Y(way),
		name,
		fantoir,
		suffixe,
		insee
FROM	(SELECT	ST_Transform(ST_SetSRID(pl.way,900913),4326) way,
				pl.name,
				pl.tags->'ref:FR:FANTOIR' fantoir,
				'' suffixe,
				p.tags->'ref:INSEE' insee
		FROM	planet_osm_polygon 	p
		JOIN	planet_osm_point 	pl
		ON		pl.way && p.way					AND
				ST_Intersects(pl.way, p.way)
		WHERE	p.tags ? 'ref:INSEE'			AND
				p.tags->'ref:INSEE'='__com__'	AND
				pl.tags->'ref:FR:FANTOIR'!=''	AND
				pl.name 	IS NOT NULL
		UNION
		SELECT	ST_Transform(ST_SetSRID(ST_Centroid(pl.way),900913),4326),
				pl.name,
				pl.tags->'ref:FR:FANTOIR' f,
				'' suffixe,
				p.tags->'ref:INSEE'
		FROM	planet_osm_polygon 	p
		JOIN	planet_osm_polygon 	pl
		ON		pl.way && p.way					AND
				ST_Intersects(pl.way, p.way)
		WHERE	p.tags ? 'ref:INSEE'			AND
				p.tags->'ref:INSEE'='__com__'	AND
--				coalesce(pl.highway,pl.tags->'ref:FR:FANTOIR') 	IS NOT NULL	AND
				(	coalesce(pl.highway,pl.tags->'ref:FR:FANTOIR') 	IS NOT NULL		OR
					pl.landuse = 'residential')	AND
				pl.name 	IS NOT NULL)a
ORDER BY 6;