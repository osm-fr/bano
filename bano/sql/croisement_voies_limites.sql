CREATE TEMP TABLE poladmin
AS
SELECT way AS geometrie,
       "ref:INSEE" AS code_insee,
       admin_level,
       name AS nom_com
FROM   planet_osm_polygon
WHERE  boundary='administrative' AND
       admin_level = 8 AND
       "ref:INSEE" LIKE '__dept__%' AND
       name != '';
-- SELECT geometrie,
--        code_insee,
--        admin_level,
--        nom AS nom_com
-- FROM   polygones_insee
-- WHERE  code_insee LIKE '__dept__%' AND
--        admin_level = '8';
CREATE INDEX gidx_poladmin ON poladmin USING GIST(geometrie);

CREATE TEMP TABLE highway_name
as
SELECT id,
       osm_id,
       way,
       ST_StartPoint(way) way_from,
       ST_EndPoint(way) way_to,
       name AS nom
FROM   (SELECT id,
               osm_id,
               way,
               name
       FROM    planet_osm_line
       WHERE   name != '' AND
               highway != '') l
JOIN poladmin
ON   way && geometrie;

CREATE INDEX gidx_highway_name_from ON highway_name USING GIST(way_from);
CREATE INDEX gidx_highway_name_to ON highway_name USING GIST(way_to);

CREATE TEMP TABLE previous_ids
AS
WITH
del
AS
(DELETE FROM croisement_voies_limites
WHERE code_dept = '__dept__'
RETURNING id,export_pbf)
SELECT id,export_pbf
FROM   del;

DELETE FROM croisement_voies_limites
WHERE code_dept = '__dept__';

INSERT INTO croisement_voies_limites
WITH
sub
AS
(SELECT DISTINCT id,
                 osm_id,
                 way,
                 nom,
                 pf.nom_com    AS nom_commune_debut,
                 pf.code_insee AS code_insee_debut,
                 pt.nom_com    AS nom_commune_fin,
                 pt.code_insee AS code_insee_fin
FROM  highway_name n
JOIN  poladmin AS pf
ON    n.way_from && pf.geometrie AND
      ST_Contains(pf.geometrie,way_from)
JOIN  poladmin AS pt
ON    n.way_to && pt.geometrie AND
      ST_Contains(pt.geometrie,way_to)
WHERE pf.code_insee != pt.code_insee)
SELECT DISTINCT '__dept__',
                id,
                osm_id,
                way,
                sub.nom,
                nom_commune_debut,
                code_insee_debut,
                COALESCE(nff.rapproche,False),
                nom_commune_fin,
                code_insee_fin,
                COALESCE(nft.rapproche,False),
                COALESCE(p.export,False)
FROM sub
LEFT JOIN (SELECT true AS export, id FROM previous_ids WHERE export_pbf) p
USING (id)
LEFT JOIN (SELECT code_insee AS code_insee_debut,nom,True AS rapproche FROM nom_fantoir WHERE code_insee LIKE '__dept__%' AND source = 'OSM') as nff
USING (code_insee_debut,nom)
LEFT JOIN (SELECT code_insee,nom,True AS rapproche FROM nom_fantoir WHERE code_insee LIKE '__dept__%' AND source = 'OSM') as nft
ON    code_insee_fin = nft.code_insee AND
      sub.nom = nft.nom;

CREATE TEMP TABLE pol_line
AS
SELECT code_insee,
       ST_Collect(ST_ExteriorRing(geom)) AS erings
FROM   (SELECT code_insee,
               (ST_Dump(geometrie)).geom AS geom
       FROM    poladmin) AS pol
GROUP BY 1;
CREATE INDEX gidx_pol ON pol_line USING GIST (erings);

DELETE FROM point_croisement_voies_limites
WHERE code_dept = '__dept__';

INSERT INTO point_croisement_voies_limites
SELECT     code_dept,
           osm_id,
           (ST_DumpPoints(ST_Intersection(geometrie_osm,erings))).geom,
           nom_osm,
           code_insee_debut,
           code_insee_fin
FROM       (SELECT * FROM croisement_voies_limites WHERE code_dept = '__dept__') c
JOIN       pol_line
ON         code_insee = code_insee_debut
UNION
SELECT     code_dept,
           osm_id,
           (ST_DumpPoints(ST_Intersection(geometrie_osm,erings))).geom,
           nom_osm,
           code_insee_debut,
           code_insee_fin
FROM       (SELECT * FROM croisement_voies_limites WHERE code_dept = '__dept__') c
JOIN       pol_line
ON         code_insee = code_insee_fin;