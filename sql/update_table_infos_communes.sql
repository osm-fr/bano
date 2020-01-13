CREATE TABLE IF NOT EXISTS infos_communes (
  dep character varying(3),
  insee_com character(5),
  name text,
  adm_weight integer,
  population integer,
  population_milliers numeric,
  type text,
  lon numeric,
  lat numeric
);

CREATE TEMP TABLE tmp_infos_communes
AS
WITH
statut
AS
(SELECT com insee_com, 1 AS statut FROM cog_commune
UNION ALL
SELECT burcentral, 2 AS statut FROM cog_canton 
UNION ALL
SELECT cheflieu, 3 AS statut FROM cog_arrondissement  
UNION ALL
SELECT cheflieu, 4 AS statut FROM cog_departement 
UNION ALL
SELECT cheflieu, 5 AS statut FROM cog_region),
adm_weight
AS
(SELECT insee_com, max(statut) AS adm_weight
FROM statut
GROUP BY 1),
pop
AS
(SELECT osm_id,
        name,
        "ref:INSEE" insee_com,
        COALESCE(population_rel,population_member,0) AS population,
        RANK() OVER(PARTITION BY "ref:INSEE" ORDER BY admin_level) rang
FROM planet_osm_communes_statut
WHERE admin_level in (8,9) AND
      boundary = 'administrative' AND
      member_role = 'admin_centre'),
pp
AS
(SELECT osm_id,
        ROUND(ST_X(ST_Transform(way,4326))::numeric,6) lon,
        ROUND(ST_Y(ST_Transform(way,4326))::numeric,6) lat
FROM planet_osm_point pp
WHERE   place != '')
SELECT cc.dep,
       adm_weight.insee_com,
       pop.name,
       adm_weight.adm_weight,
       pop.population,
       ROUND((pop.population::numeric/1000),1) AS population_milliers,
       CASE 
         WHEN pop.population < 1000 THEN 'village'
         WHEN pop.population < 10000 THEN 'town'
         ELSE 'city'
       END AS type,
       pp.lon,
       pp.lat
FROM adm_weight
JOIN cog_commune cc
ON cc.com = insee_com
LEFT OUTER JOIN pop
USING (insee_com)
JOIN  pp
USING (osm_id)
WHERE pop.rang = 1;

TRUNCATE TABLE infos_communes;
INSERT INTO infos_communes
SELECT *
FROM tmp_infos_communes;