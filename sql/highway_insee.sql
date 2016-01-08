WITH
f
AS
(	SELECT	pl.name as namecomp,
			unnest(array[pl.name,pl.tags->'alt_name',pl.tags->'old_name']) as name,
			pl.tags->'ref:FR:FANTOIR' f,
			'' fl,
			'' fr,
			'' suffixe,
			p.tags->'ref:INSEE' insee
	FROM	planet_osm_polygon 	p
	JOIN	planet_osm_point 	pl
	ON		pl.way && p.way					AND
			ST_Intersects(pl.way, p.way)
	WHERE	p.tags ? 'ref:INSEE'			AND
			p.tags->'ref:INSEE'='__com__'	AND
			pl.tags->'ref:FR:FANTOIR'!=''			AND
			pl.name 	IS NOT NULL
	UNION
	SELECT	l.name,
			unnest(array[l.name,l.tags->'alt_name',l.tags->'old_name']),
			l.tags->'ref:FR:FANTOIR' f,
			l.tags->'ref:FR:FANTOIR:left' fl,
			l.tags->'ref:FR:FANTOIR:right' fr,
			'' suffixe,p.tags->'ref:INSEE'
	FROM	planet_osm_polygon 	p
	JOIN	planet_osm_line 	l
	ON		ST_Intersects(l.way, p.way)
	WHERE	p.tags ? 'ref:INSEE'			AND
			p.tags->'ref:INSEE'='__com__'	AND
			l.highway 	IS NOT NULL			AND
			l.name 		IS NOT NULL
	UNION
	SELECT	pl.name,
			unnest(array[pl.name,pl.tags->'alt_name',pl.tags->'old_name']),
			pl.tags->'ref:FR:FANTOIR' f,
			'' fl,
			'' fr,
			'' suffixe,
			p.tags->'ref:INSEE'
	FROM	planet_osm_polygon 	p
	JOIN	planet_osm_polygon 	pl
	ON		pl.way && p.way					AND
			ST_Intersects(pl.way, p.way)
	WHERE	p.tags ? 'ref:INSEE'			AND
			p.tags->'ref:INSEE'='__com__'	AND
			(	coalesce(pl.highway,pl.tags->'ref:FR:FANTOIR') 	IS NOT NULL		OR
				pl.landuse = 'residential'										OR
				pl.amenity = 'parking')		AND
			pl.name 	IS NOT NULL)
SELECT 	name,
		CASE
			WHEN name = namecomp THEN f
			ELSE NULL
		END f,
		CASE
			WHEN name = namecomp THEN fl
			ELSE NULL
		END fl,
		CASE
			WHEN name = namecomp THEN fr
			ELSE NULL
		END fr,
		suffixe,
		insee
FROM 	f
WHERE	name IS NOT NULL
ORDER BY 6;