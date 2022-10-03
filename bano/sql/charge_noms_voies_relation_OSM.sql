WITH
a
AS
(SELECT	DISTINCT unnest(array[l.name,l.tags->'alt_name',l.tags->'old_name']) as name,
	    l.way,
		r.tags,
--		h.libelle_suffixe,
--		a9.code_insee,
--		a9.nom,
		'voie'::text
FROM	(SELECT way FROM planet_osm_polygon WHERE "ref:INSEE" = '__code_insee__')	p
JOIN	(SELECT name,tags,osm_id,way FROM planet_osm_line WHERE highway != '' AND name != '') l
ON		ST_Intersects(l.way, p.way)
JOIN	planet_osm_rels		r
ON		r.osm_id = l.osm_id),
/*LEFT OUTER JOIN (SELECT * FROM suffixe WHERE code_insee = '__code_insee__') h
ON		ST_Intersects(l.way, h.geometrie)
LEFT OUTER JOIN (SELECT * FROM polygones_insee_a9 where insee_a8 = '__code_insee__') a9
ON		ST_Contains(a9.geometrie,l.way)*/
b
as
(SELECT	DISTINCT unnest(array[l.name,l.tags->'alt_name',l.tags->'old_name']) as name,
	    l.way,
		r.tags,
--		h.libelle_suffixe,
--		a9.code_insee,
--		a9.nom,
		'voie'::text
FROM	(SELECT way FROM planet_osm_polygon WHERE "ref:INSEE" = '__code_insee__')	p
JOIN	(SELECT name,tags,osm_id,way FROM planet_osm_polygon WHERE highway != '' AND name != '') l
ON		ST_Intersects(l.way, p.way)
JOIN	planet_osm_rels		r
ON		r.osm_id = l.osm_id)
select a.name,
       a.tags,
		h.libelle_suffixe,
		a9.code_insee,
		a9.nom
from a
LEFT OUTER JOIN (SELECT * FROM suffixe WHERE code_insee = '__code_insee__') h
ON		ST_Intersects(way, h.geometrie)
LEFT OUTER JOIN (SELECT * FROM polygones_insee_a9 where insee_a8 = '__code_insee__') a9
ON		ST_Contains(a9.geometrie,way)
WHERE a.name IS NOT NULL
union
select b.name,
       b.tags,
		h.libelle_suffixe,
		a9.code_insee,
		a9.nom
from b
LEFT OUTER JOIN (SELECT * FROM suffixe WHERE code_insee = '__code_insee__') h
ON		ST_Intersects(way, h.geometrie)
LEFT OUTER JOIN (SELECT * FROM polygones_insee_a9 where insee_a8 = '__code_insee__') a9
ON		ST_Contains(a9.geometrie,way)
WHERE b.name IS NOT NULL
;