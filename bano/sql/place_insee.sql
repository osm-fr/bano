DELETE FROM place_insee WHERE insee_com = '__com__';
WITH
a AS
(SELECT	ST_Transform(pt.way,4326) pt_geo,
		pt.place,
		pt.name,
		pt."ref:FR:FANTOIR" fantoir,
		pt.tags,
		p."ref:INSEE" insee_com
 FROM	planet_osm_polygon	p
 JOIN	planet_osm_point 	pt
 ON		ST_Intersects(pt.way, p.way)
 WHERE	p."ref:INSEE" = '__com__'	AND
        (pt.place != ''                                       OR
        (pt.railway !='' AND pt."ref:FR:FANTOIR" != '') OR
        (pt.amenity !='' AND pt."ref:FR:FANTOIR" != '')    ) AND
		pt.name != '')
INSERT INTO place_insee
SELECT 	ST_X(pt_geo),
		ST_Y(pt_geo),
		place,
		name,
		fantoir,
		'0', --ld_bati
		tags,
		insee_com,
        round(extract(epoch from now()))
FROM	a;
COMMIT;