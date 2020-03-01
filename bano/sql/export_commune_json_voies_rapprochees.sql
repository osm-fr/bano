WITH
osm
AS
(SELECT geometrie,
             insee_com,
             voie_cadastre,
             voie_osm,
             fantoir,
             numero,
             RANK() OVER (PARTITION BY fantoir,numero ORDER BY source DESC) rang
      FROM   cumul_adresses
      WHERE  insee_com = '$com'),
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
          WHERE cc.com = '$com')
SELECT json_build_object('id',
                         osm.fantoir || CASE WHEN coalesce(cp.postal_code, lp.cp)!=lp.cp THEN ('_' || cp.postal_code) ELSE '' END,
                         'citycode',
                         osm.insee_com,
                         'type',
                         'street',                                 
                         'name',
                         replace(replace(v.voie_osm,'\"',''),'’',chr(39)),
                         'postcode',
                         coalesce(cp.postal_code, min(lp.cp)),
                         'post_office',
                         CASE WHEN replace(lower(cp.name),'-',' ') != replace(lower(c.name),'-',' ') THEN cp.name ELSE c.name END,
                         'lat',
                         round(st_y(v.geometrie)::numeric,6),
                         'lon',
                         round(st_x(v.geometrie)::numeric,6),
                         'city',
                         c.name,
                         'departement',
                         cog.nom_dep,
                         'region',
                         cog.nom_reg,
                         'importance',
                         round(log(c.adm_weight+log(c.population+1)/3)::numeric*log(1+log(count(osm.*)+1)+log(st_length(st_longestline(st_convexhull(ST_Collect(osm.geometrie)),st_convexhull(ST_Collect(osm.geometrie)))::geography)+1)+log(CASE WHEN v.voie_osm like 'Boulevard%' THEN 4 WHEN v.voie_osm LIKE 'Place%' THEN 4 WHEN v.voie_osm LIKE 'Espl%' THEN 4 WHEN v.voie_osm LIKE 'Av%' THEN 3 WHEN v.voie_osm LIKE 'Rue %' THEN 2 ELSE 1 END))::numeric,4),
                         'housenumbers',
                         translate((json_agg(json_build_object(numero,json_build_object('lon',st_x(osm.geometrie),'lat',st_y(osm.geometrie))))::text),'[]',''))
FROM cumul_voies v
JOIN infos_communes c
ON (c.insee_com=v.insee_com)
JOIN osm
ON osm.fantoir=v.fantoir
LEFT JOIN cog
ON v.insee_com = cog.insee
LEFT JOIN codes_postaux lp
ON (lp.insee=v.insee_com)
LEFT JOIN planet_osm_postal_code cp
ON (cp."ref:INSEE"=v.insee_com AND
  ST_Contains(cp.way, osm.geometrie))
WHERE v.insee_com = '$com' AND
      osm.numero ~ '^[0-9]{1,4}( ?[A-Z]?.*)?' AND
      osm.numero !~'.[0-9 \\.\\-]{9,}'
GROUP BY osm.fantoir,
         osm.insee_com,
         v.voie_osm,
         v.geometrie,
         cp.postal_code,
         lp.cp,
         c.name,
         cp.name,
         cog.nom_dep,
         cog.nom_reg,
         c.adm_weight,
         c.population
ORDER BY osm.fantoir;
