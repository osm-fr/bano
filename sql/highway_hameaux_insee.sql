SELECT	l.name,l.tags->'ref:FR:FANTOIR' f,l.tags->'ref:FR:FANTOIR:left' fl,l.tags->'ref:FR:FANTOIR:right' fr,h.hameau
		FROM	planet_osm_polygon 	p
		JOIN	planet_osm_line 	l
		ON		ST_Intersects(l.way, p.way)
		LEFT OUTER  JOIN (SELECT ST_Transform(ST_PolygonFromText('POLYGON((3.971706 43.54037,3.970234 43.54127,3.968734 43.54277,3.970603 43.54653,3.970809 43.54691,3.972309 43.54841,3.973098 43.5488,3.978088 43.55024,3.992907 43.5532,4.00644 43.55405,4.007098 43.55409,4.008598 43.55259,4.007098 43.55109,4.002757 43.54945,3.971706 43.54037))',4326),900913) geom,'Carnon'::text hameau) h
		ON		ST_Intersects(l.way, h.geom)
		WHERE	p.tags ? 'ref:INSEE'			AND
				p.tags->'ref:INSEE'='34154'	AND
				l.highway 	IS NOT NULL			AND
				l.name 		IS NOT NULL
				group by 1,2,3,4,5
UNION
SELECT	pl.name,pl.tags->'ref:FR:FANTOIR' f,pl.tags->'ref:FR:FANTOIR:left' fl,pl.tags->'ref:FR:FANTOIR:right' fr
		FROM	planet_osm_polygon 	p
		JOIN	planet_osm_polygon 	pl
		ON		pl.way && p.way					AND
				ST_Intersects(pl.way, p.way)
		WHERE	p.tags ? 'ref:INSEE'			AND
				p.tags->'ref:INSEE'='__com__'	AND
				pl.highway 	IS NOT NULL			AND
				pl.name 	IS NOT NULL
				group by 1,2,3,4
				;