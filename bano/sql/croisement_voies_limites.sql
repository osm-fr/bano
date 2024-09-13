CREATE TEMP TABLE poladmin
AS
SELECT geometrie,code_insee,admin_level,nom 
FROM   polygones_insee
WHERE  code_insee LIKE '__dept__%' AND
       admin_level = '8';
CREATE INDEX gidx_poladmin ON poladmin USING GIST(geometrie);

CREATE TEMP TABLE highway_name
as
SELECT osm_id,
       ST_StartPoint(way) way_from,
       ST_EndPoint(way) way_to,
       name
FROM   (SELECT osm_id,
	           way,
	           highway,
	           name
	   FROM    planet_osm_line 
	   WHERE   name != '' AND
	           highway != '') l
JOIN poladmin
ON   way && geometrie;

CREATE INDEX gidx_highway_name_from ON highway_name USING GIST(way_from);
CREATE INDEX gidx_highway_name_to ON highway_name USING GIST(way_to);

-- DROP TABLE IF EXISTS highway_name_overlap CASCADE;
-- CREATE TEMP TABLE highway_name_overlap
-- 	as

DELETE FROM croisement_voies_limites
WHERE code_dept = '__dept__';

INSERT INTO croisement_voies_limites
SELECT DISTINCT '__dept__',
                osm_id,
                l.way,
                n.name,
                way_from,
                pf.nom,
                pf.code_insee,
                way_to,
                pt.nom,
                pt.code_insee
FROM  highway_name n
JOIN  planet_osm_line l
USING (osm_id)
JOIN  poladmin AS pf
ON    n.way_from && pf.geometrie AND
      ST_Contains(pf.geometrie,way_from)
JOIN  poladmin AS pt
ON    n.way_to && pt.geometrie AND
      ST_Contains(pt.geometrie,way_to)
WHERE pf.code_insee != pt.code_insee;