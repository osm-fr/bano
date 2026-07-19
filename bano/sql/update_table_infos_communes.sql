CREATE TEMP TABLE tmp_infos_communes
AS
WITH
statut
AS
(SELECT com code_insee, 1 AS statut FROM cog_commune
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
(SELECT code_insee, max(statut) AS adm_weight
FROM statut
GROUP BY 1),
pop
AS
(SELECT osm_id,
        name,
        "ref:INSEE" code_insee,
        COALESCE(population_rel,population_member,0) AS population,
        RANK() OVER(PARTITION BY "ref:INSEE" ORDER BY admin_level) rang
FROM planet_osm_communes_statut
WHERE admin_level in (8,9) AND
      boundary = 'administrative' AND
      member_role = 'admin_centre'),
pp
AS
(SELECT osm_id,
        ROUND(ST_X(way)::numeric,6) lon,
        ROUND(ST_Y(way)::numeric,6) lat,
        way AS geometrie
FROM planet_osm_point pp
WHERE   place != '')
SELECT cc.dep,
       adm_weight.code_insee,
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
       pp.lat,
       pp.geometrie
FROM adm_weight
JOIN cog_commune cc
ON cc.com = code_insee
LEFT OUTER JOIN pop
USING (code_insee)
LEFT OUTER JOIN  pp
USING (osm_id)
WHERE (pop.rang IS NULL OR pop.rang = 1) AND
      cc.typecom != 'COMD';

TRUNCATE TABLE infos_communes;
INSERT INTO infos_communes
SELECT *
FROM tmp_infos_communes;
