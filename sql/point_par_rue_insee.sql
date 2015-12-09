SELECT	ST_x(point),
		ST_y(point),
		name,
		insee
FROM (	WITH w
		AS (SELECT	l.way,
					l.name,
					p.tags->'ref:INSEE' insee
			FROM	planet_osm_polygon p
			JOIN	planet_osm_line l
			ON		ST_Intersects(l.way, p.way)
			WHERE	p.tags ? 'ref:INSEE'			AND
					p.tags->'ref:INSEE'='__com__'	AND
					(l.highway IS NOT NULL			OR
					l.waterway = 'dam')				AND
					l.name IS NOT NULL)
		SELECT	ST_Transform(ST_SetSRID(ST_ClosestPoint(wl.way,wp.way),900913),4326) point,
				wl.name,
				wl.insee
		FROM	(SELECT ST_LineMerge(st_collect(way)) way,
						name,
						insee
				FROM	w
				GROUP BY 2,3) wl
		JOIN	(SELECT ST_Centroid(ST_LineMerge(ST_Collect(way))) way,
						name
				FROM	w
				GROUP BY 2) wp
		ON		wl.name = wp.name) a;

