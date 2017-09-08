WITH w0
AS (SELECT	l.way,
		unnest(array[l.name,l.tags->'alt_name',l.tags->'old_name']) as name,
		p.tags->'ref:INSEE' as insee,
		ST_Within(l.way,p.way)::integer as within
	FROM	planet_osm_polygon p
	JOIN	planet_osm_line l
	ON	ST_Intersects(l.way, p.way)
	WHERE	p.tags ? 'ref:INSEE'		AND
		p.tags->'ref:INSEE'='__com__'	AND
		(l.highway IS NOT NULL		OR
		l.waterway = 'dam')		AND
		l.name IS NOT NULL),
w1
AS
(SELECT *
FROM 	w0
WHERE 	name IS NOT NULL),
w2
AS
(SELECT	*,rank() OVER(PARTITION BY name,insee ORDER BY within DESC) rang
FROM	w1),
wl
AS
(SELECT ST_LineMerge(st_collect(way)) way,
		name,
		insee
	FROM	w2
	WHERE	rang = 1
	GROUP BY 2,3),
wp
AS
(SELECT ST_Centroid(ST_LineMerge(ST_Collect(way))) way,
		name
	FROM	w2
	WHERE 	rang = 1
	GROUP BY 2),
a
AS
(SELECT	ST_Transform(ST_SetSRID(ST_ClosestPoint(wl.way,wp.way),900913),4326) point,
		wl.name,
		wl.insee
FROM	wl
JOIN	wp
ON		wl.name = wp.name) 

SELECT	ST_x(point),
		ST_y(point),
		name,
		insee
FROM 	a;
