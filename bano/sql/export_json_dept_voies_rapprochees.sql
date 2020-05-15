WITH
sort_order
AS
(SELECT 1::integer as sortnum, 'OSM' as source
UNION ALL
SELECT 2,'BAL'
UNION ALL
SELECT 3,'CADASTRE'
),
pre_osm
AS
(SELECT geometrie,
        insee_com,
        fantoir,
        REPLACE(REPLACE(numero,'\',';'),'"','') AS numero,
        code_postal,
        source
FROM    cumul_adresses
WHERE   dept = '__dept__'),
osm
AS
(SELECT geometrie,
        insee_com,
        fantoir,
        numero,
        code_postal,
        ROW_NUMBER() OVER (PARTITION BY fantoir,numero ORDER BY sortnum) rang
FROM    pre_osm
JOIN    sort_order USING (source)),
osm_postal
AS
(SELECT o.geometrie,
        o.insee_com,
--        o.voie_osm,
        o.fantoir,
        o.numero,
        COALESCE(o.code_postal,pp.code_postal) code_postal,
        RANK() OVER(PARTITION BY o.fantoir,o.numero ORDER BY id) rang_postal
FROM osm o
JOIN polygones_postaux pp
ON ST_Contains(pp.geometrie, o.geometrie)
WHERE o.rang = 1),
cog
AS
(SELECT cc.com AS insee,
                  cd.libelle AS nom_dep,
                  cr.libelle AS nom_reg
          FROM cog_commune cc
          JOIN cog_departement cd
          USING (dep)
          JOIN cog_region cr
          ON cc.reg = cr.reg
          WHERE cc.dep = '__dept__')
SELECT osm_postal.fantoir, --|| CASE WHEN coalesce(cp.postal_code, lp.cp)!=lp.cp THEN ('_' || cp.postal_code) ELSE '' END AS id,
       osm_postal.insee_com AS citycode,
       'street' AS type,
       REPLACE(REPLACE(REGEXP_REPLACE(v.voie_osm,'\t',' '),'"',chr(39)),'’',chr(39)) AS name,
       osm_postal.code_postal AS postcode,
       round(st_y(v.geometrie)::numeric,6) AS lat,
       round(st_x(v.geometrie)::numeric,6) AS lon,
       c.name AS city,
       cog.nom_dep AS departement,
       cog.nom_reg AS region,
       round(log(c.adm_weight+log(c.population+1)/3)::numeric*log(1+log(count(osm_postal.*)+1)+log(st_length(st_longestline(st_convexhull(ST_Collect(osm_postal.geometrie)),st_convexhull(ST_Collect(osm_postal.geometrie)))::geography)+1)+log(CASE WHEN v.voie_osm like 'Boulevard%' THEN 4 WHEN v.voie_osm LIKE 'Place%' THEN 4 WHEN v.voie_osm LIKE 'Espl%' THEN 4 WHEN v.voie_osm LIKE 'Av%' THEN 3 WHEN v.voie_osm LIKE 'Rue %' THEN 2 ELSE 1 END))::numeric,4) AS importance,
       string_agg(numero||'$'||st_y(osm_postal.geometrie)||'$'||st_x(osm_postal.geometrie),'#' ORDER BY numero)::text AS housenumbers
FROM cumul_voies v
JOIN infos_communes c
ON (c.insee_com=v.insee_com)
JOIN osm_postal
ON osm_postal.fantoir=v.fantoir
LEFT JOIN cog
ON v.insee_com = cog.insee
WHERE v.dept = '__dept__' AND
      osm_postal.rang_postal = 1 AND
      osm_postal.numero ~ '^[0-9]{1,4}( ?[A-Z]?.*)?' AND
      osm_postal.numero !~'.[0-9 \\.\\-]{9,}'
GROUP BY osm_postal.fantoir,
         osm_postal.insee_com,
         osm_postal.code_postal,
         v.voie_osm,
         v.geometrie,
         c.name,
         cog.nom_dep,
         cog.nom_reg,
         c.adm_weight,
         c.population
ORDER BY osm_postal.fantoir;

