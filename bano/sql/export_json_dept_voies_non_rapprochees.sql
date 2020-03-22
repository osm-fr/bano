/*WITH
v
AS
(SELECT   code_insee AS insee_com,
          fantoir10 AS fantoir
FROM      fantoir_voie f
WHERE code_dept = '__dept__'
EXCEPT
SELECT insee_com,fantoir
FROM cumul_voies v 
WHERE dept = '__dept__'),
osm
AS
(SELECT geometrie,
             insee_com,
             COALESCE(voie_bal,voie_cadastre) voie,
             fantoir,
             numero,
             RANK() OVER (PARTITION BY fantoir,numero ORDER BY source DESC) rang
      FROM   cumul_adresses
      WHERE  dept = '__dept__'),
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
          WHERE cd.dep = '__dept__')
-- SELECT json_build_object('id',
--                          osm.fantoir || CASE WHEN coalesce(cp.postal_code, lp.cp)!=lp.cp THEN ('_' || cp.postal_code) ELSE '' END,
--                          'citycode',
--                          osm.insee_com,
--                          'type',
--                          'street',
--                          'name',
--                          replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(max(case when osm.voie_osm !='' then osm.voie_osm else osm.voie_cadastre end),'^IMP ','Impasse '),'^RTE ','Route '),'^ALL ','Allée '),'^PL ','Place '),'^PLA ','Place '),'^AV ','Avenue '),'^LOT ','Lotissement '),'^RES ','Résidence '),'^CHEM ','Chemin '),'^RLE ','Ruelle '),'^BD ','Boulevard '),'^SQ ','Square '),'^PAS ','Passage '),'^SEN ','Sentier '),'^CRS ','Cours '),'^TRA ','Traverse '),'^MTE ','Montée '),'^RPT ','Rond-point '),'^HAM ','Hameau '),'^VLA ','Villa '),'^PROM ','Promenade '),'^ESP ','Esplanade '),'^FG ','Faubourg '),'^TSSE ','Terrasse '),'^CTRE ','Centre '),'^PASS ','Passerelle '),'^FRM ','Ferme '),' GAL ',' Général '),' MAL ',' Maréchal '),' ST ',' Saint '),' STE ',' Sainte '),' PDT ',' Président '),' HT ',' Haut '),' HTE ',' Haute '),' VX ',' Vieux '),' PTE ',' Petite '),'\"',''),'’',chr(39)),
--                          'postcode',
--                          coalesce(cp.postal_code, min(lp.cp)),
--                          'post_office',
--                          CASE WHEN replace(lower(cp.name),'-',' ') != replace(lower(c.name),'-',' ') THEN cp.name ELSE c.name END,
--                          'lat',
--                          round(st_y(st_centroid(st_convexhull(ST_Collect(osm.geometrie))))::numeric,6),
--                          'lon',
--                          round(st_x(st_centroid(st_convexhull(ST_Collect(osm.geometrie))))::numeric,6),
--                          'city',
--                          c.name,
--                          'departement',
--                          cog.nom_dep,
--                          'region',
--                          cog.nom_reg,
--                          'importance',
--                          round(log(c.adm_weight+log(c.population+1)/3)::numeric*log(1+log(count(osm.*)+1)+log(st_length(st_longestline(st_convexhull(ST_Collect(osm.geometrie)),st_convexhull(ST_Collect(osm.geometrie)))::geography)+1)+log(CASE WHEN voie like 'Boulevard%' THEN 4 WHEN voie LIKE 'Place%' THEN 4 WHEN voie LIKE 'Espl%' THEN 4 WHEN voie LIKE 'Av%' THEN 3 WHEN voie LIKE 'Rue %' THEN 2 ELSE 1 END))::numeric,4),
--                          'housenumbers',
--                          translate((json_agg(json_build_object(numero,json_build_object('lon',st_x(osm.geometrie),'lat',st_y(osm.geometrie))))::text),'[]',''))
SELECT  osm.fantoir || CASE WHEN coalesce(cp.postal_code, lp.cp)!=lp.cp THEN ('_' || cp.postal_code) ELSE '' END as id,
        osm.insee_com as citycode,
        'street' as type,
        replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(voie,'^IMP ','Impasse '),'^RTE ','Route '),'^ALL ','Allée '),'^PL ','Place '),'^PLA ','Place '),'^AV ','Avenue '),'^LOT ','Lotissement '),'^RES ','Résidence '),'^CHEM ','Chemin '),'^RLE ','Ruelle '),'^BD ','Boulevard '),'^SQ ','Square '),'^PAS ','Passage '),'^SEN ','Sentier '),'^CRS ','Cours '),'^TRA ','Traverse '),'^MTE ','Montée '),'^RPT ','Rond-point '),'^HAM ','Hameau '),'^VLA ','Villa '),'^PROM ','Promenade '),'^ESP ','Esplanade '),'^FG ','Faubourg '),'^TSSE ','Terrasse '),'^CTRE ','Centre '),'^PASS ','Passerelle '),'^FRM ','Ferme '),' GAL ',' Général '),' MAL ',' Maréchal '),' ST ',' Saint '),' STE ',' Sainte '),' PDT ',' Président '),' HT ',' Haut '),' HTE ',' Haute '),' VX ',' Vieux '),' PTE ',' Petite '),'\"',''),'’',chr(39)) AS name,
        coalesce(cp.postal_code, min(lp.cp)) AS postcode,
        CASE WHEN replace(lower(cp.name),'-',' ') != replace(lower(c.name),'-',' ') THEN cp.name ELSE c.name END AS post_office,
       round(st_y(st_centroid(st_convexhull(ST_Collect(osm.geometrie))))::numeric,6) AS lat,
       round(st_x(st_centroid(st_convexhull(ST_Collect(osm.geometrie))))::numeric,6) AS lon,
       c.name AS city,
       cog.nom_dep AS departement,
       cog.nom_reg AS region,
       round(log(c.adm_weight+log(c.population+1)/3)::numeric*log(1+log(count(osm.*)+1)+log(st_length(st_longestline(st_convexhull(ST_Collect(osm.geometrie)),st_convexhull(ST_Collect(osm.geometrie)))::geography)+1)+log(CASE WHEN voie like 'Boulevard%' THEN 4 WHEN voie LIKE 'Place%' THEN 4 WHEN voie LIKE 'Espl%' THEN 4 WHEN voie LIKE 'Av%' THEN 3 WHEN voie LIKE 'Rue %' THEN 2 ELSE 1 END))::numeric,4) AS importance,
       translate((json_agg(json_build_object(numero,json_build_object('lon',st_x(osm.geometrie),'lat',st_y(osm.geometrie))))::text),'[]','') AS housenumbers
FROM v
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
WHERE osm.numero ~ '^[0-9]{1,4}( ?[A-Z]?.*)?' AND
      osm.numero !~'.[0-9 \\.\\-]{9,}'
GROUP BY osm.fantoir,
         osm.insee_com,
         osm.voie,
         cp.postal_code,
         lp.cp,
         c.name,
         cp.name,
         cog.nom_dep,
         cog.nom_reg,
         c.adm_weight,
         c.population
ORDER BY osm.fantoir;



WITH
v
AS
(SELECT   code_insee AS insee_com,
          fantoir10 AS fantoir
FROM      fantoir_voie f
WHERE code_dept = '92'
EXCEPT
SELECT insee_com,fantoir
FROM cumul_voies v 
WHERE dept = '92'),
osm
AS
(SELECT geometrie,
             insee_com,
             COALESCE(voie_bal,voie_cadastre) voie,
             fantoir,
             numero,
             code_postal,
             RANK() OVER (PARTITION BY fantoir,numero ORDER BY source DESC) rang
      FROM   cumul_adresses
      WHERE  dept = '92'),
osm_postal
AS
(SELECT o.geometrie,
        o.insee_com,
        o.voie,
        o.fantoir,
        o.numero,
        COALESCE(o.code_postal,pp.code_postal) code_postal,
        RANK() OVER(PARTITION BY o.fantoir,o.numero ORDER BY id) rang
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
          WHERE cd.dep = '92')
-- SELECT json_build_object('id',
--                          osm.fantoir || CASE WHEN coalesce(cp.postal_code, lp.cp)!=lp.cp THEN ('_' || cp.postal_code) ELSE '' END,
--                          'citycode',
--                          osm.insee_com,
--                          'type',
--                          'street',
--                          'name',
--                          replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(max(case when osm.voie_osm !='' then osm.voie_osm else osm.voie_cadastre end),'^IMP ','Impasse '),'^RTE ','Route '),'^ALL ','Allée '),'^PL ','Place '),'^PLA ','Place '),'^AV ','Avenue '),'^LOT ','Lotissement '),'^RES ','Résidence '),'^CHEM ','Chemin '),'^RLE ','Ruelle '),'^BD ','Boulevard '),'^SQ ','Square '),'^PAS ','Passage '),'^SEN ','Sentier '),'^CRS ','Cours '),'^TRA ','Traverse '),'^MTE ','Montée '),'^RPT ','Rond-point '),'^HAM ','Hameau '),'^VLA ','Villa '),'^PROM ','Promenade '),'^ESP ','Esplanade '),'^FG ','Faubourg '),'^TSSE ','Terrasse '),'^CTRE ','Centre '),'^PASS ','Passerelle '),'^FRM ','Ferme '),' GAL ',' Général '),' MAL ',' Maréchal '),' ST ',' Saint '),' STE ',' Sainte '),' PDT ',' Président '),' HT ',' Haut '),' HTE ',' Haute '),' VX ',' Vieux '),' PTE ',' Petite '),'\"',''),'’',chr(39)),
--                          'postcode',
--                          coalesce(cp.postal_code, min(lp.cp)),
--                          'post_office',
--                          CASE WHEN replace(lower(cp.name),'-',' ') != replace(lower(c.name),'-',' ') THEN cp.name ELSE c.name END,
--                          'lat',
--                          round(st_y(st_centroid(st_convexhull(ST_Collect(osm.geometrie))))::numeric,6),
--                          'lon',
--                          round(st_x(st_centroid(st_convexhull(ST_Collect(osm.geometrie))))::numeric,6),
--                          'city',
--                          c.name,
--                          'departement',
--                          cog.nom_dep,
--                          'region',
--                          cog.nom_reg,
--                          'importance',
--                          round(log(c.adm_weight+log(c.population+1)/3)::numeric*log(1+log(count(osm.*)+1)+log(st_length(st_longestline(st_convexhull(ST_Collect(osm.geometrie)),st_convexhull(ST_Collect(osm.geometrie)))::geography)+1)+log(CASE WHEN voie like 'Boulevard%' THEN 4 WHEN voie LIKE 'Place%' THEN 4 WHEN voie LIKE 'Espl%' THEN 4 WHEN voie LIKE 'Av%' THEN 3 WHEN voie LIKE 'Rue %' THEN 2 ELSE 1 END))::numeric,4),
--                          'housenumbers',
--                          translate((json_agg(json_build_object(numero,json_build_object('lon',st_x(osm.geometrie),'lat',st_y(osm.geometrie))))::text),'[]',''))
SELECT osm_postal.fantoir || CASE WHEN coalesce(osm_postal.code_postal, lp.cp)!=lp.cp THEN ('_' || osm_postal.code_postal) ELSE '' END as id,
       osm_postal.insee_com as citycode,
       'street' as type,
       replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(voie,'^IMP ','Impasse '),'^RTE ','Route '),'^ALL ','Allée '),'^PL ','Place '),'^PLA ','Place '),'^AV ','Avenue '),'^LOT ','Lotissement '),'^RES ','Résidence '),'^CHEM ','Chemin '),'^RLE ','Ruelle '),'^BD ','Boulevard '),'^SQ ','Square '),'^PAS ','Passage '),'^SEN ','Sentier '),'^CRS ','Cours '),'^TRA ','Traverse '),'^MTE ','Montée '),'^RPT ','Rond-point '),'^HAM ','Hameau '),'^VLA ','Villa '),'^PROM ','Promenade '),'^ESP ','Esplanade '),'^FG ','Faubourg '),'^TSSE ','Terrasse '),'^CTRE ','Centre '),'^PASS ','Passerelle '),'^FRM ','Ferme '),' GAL ',' Général '),' MAL ',' Maréchal '),' ST ',' Saint '),' STE ',' Sainte '),' PDT ',' Président '),' HT ',' Haut '),' HTE ',' Haute '),' VX ',' Vieux '),' PTE ',' Petite '),'\"',''),'’',chr(39)) AS name,
       osm_postal.code_postal AS postcode,
       CASE WHEN replace(lower(lp.libelle),'-',' ') != replace(lower(c.name),'-',' ') THEN lp.libelle ELSE c.name END AS post_office,
       round(st_y(st_centroid(st_convexhull(ST_Collect(osm_postal.geometrie))))::numeric,6) AS lat,
       round(st_x(st_centroid(st_convexhull(ST_Collect(osm_postal.geometrie))))::numeric,6) AS lon,
       c.name AS city,
       cog.nom_dep AS departement,
       cog.nom_reg AS region,
       round(log(c.adm_weight+log(c.population+1)/3)::numeric*log(1+log(count(osm_postal.*)+1)+log(st_length(st_longestline(st_convexhull(ST_Collect(osm_postal.geometrie)),st_convexhull(ST_Collect(osm_postal.geometrie)))::geography)+1)+log(CASE WHEN voie like 'Boulevard%' THEN 4 WHEN voie LIKE 'Place%' THEN 4 WHEN voie LIKE 'Espl%' THEN 4 WHEN voie LIKE 'Av%' THEN 3 WHEN voie LIKE 'Rue %' THEN 2 ELSE 1 END))::numeric,4) AS importance,
       translate((json_agg(json_build_object(numero,json_build_object('lon',st_x(osm_postal.geometrie),'lat',st_y(osm_postal.geometrie))))::text),'[]','') AS housenumbers
FROM v
JOIN infos_communes c
ON (c.insee_com=v.insee_com)
JOIN osm_postal
ON osm_postal.fantoir=v.fantoir
LEFT JOIN cog
ON v.insee_com = cog.insee
LEFT JOIN codes_postaux lp
ON (lp.insee=v.insee_com)
--LEFT JOIN polygones_postaux cp
--ON ST_Contains(cp.geometrie, osm.geometrie)
WHERE osm_postal.numero ~ '^[0-9]{1,4}( ?[A-Z]?.*)?' AND
      osm_postal.numero !~'.[0-9 \\.\\-]{9,}' AND
      osm_postal.rang = 1
GROUP BY osm_postal.fantoir,
         osm_postal.insee_com,
         osm_postal.voie,
         osm_postal.code_postal,
         lp.cp,
         c.name,
         lp.libelle,
         cog.nom_dep,
         cog.nom_reg,
         c.adm_weight,
         c.population
ORDER BY osm_postal.fantoir;
*/

WITH
v
AS
(SELECT   code_insee AS insee_com,
          fantoir10 AS fantoir
FROM      fantoir_voie f
WHERE code_dept = '__dept__'
EXCEPT
SELECT insee_com,fantoir
FROM cumul_voies v 
WHERE dept = '__dept__'),
osm
AS
(SELECT c.geometrie,
             c.insee_com,
             COALESCE(voie_bal,voie_cadastre) voie,
             c.fantoir,
             c.numero,
             c.code_postal,
             source,
             RANK() OVER (PARTITION BY c.fantoir,c.numero ORDER BY c.source DESC) rang
      FROM   cumul_adresses c
      JOIN   v
      USING (fantoir)
      WHERE  dept = '__dept__'),
osm_postal
AS
(SELECT o.geometrie,
        o.insee_com,
        o.voie,
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
          WHERE cd.dep = '__dept__')
-- SELECT json_build_object('id',
--                          osm.fantoir || CASE WHEN coalesce(cp.postal_code, lp.cp)!=lp.cp THEN ('_' || cp.postal_code) ELSE '' END,
--                          'citycode',
--                          osm.insee_com,
--                          'type',
--                          'street',
--                          'name',
--                          replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(max(case when osm.voie_osm !='' then osm.voie_osm else osm.voie_cadastre end),'^IMP ','Impasse '),'^RTE ','Route '),'^ALL ','Allée '),'^PL ','Place '),'^PLA ','Place '),'^AV ','Avenue '),'^LOT ','Lotissement '),'^RES ','Résidence '),'^CHEM ','Chemin '),'^RLE ','Ruelle '),'^BD ','Boulevard '),'^SQ ','Square '),'^PAS ','Passage '),'^SEN ','Sentier '),'^CRS ','Cours '),'^TRA ','Traverse '),'^MTE ','Montée '),'^RPT ','Rond-point '),'^HAM ','Hameau '),'^VLA ','Villa '),'^PROM ','Promenade '),'^ESP ','Esplanade '),'^FG ','Faubourg '),'^TSSE ','Terrasse '),'^CTRE ','Centre '),'^PASS ','Passerelle '),'^FRM ','Ferme '),' GAL ',' Général '),' MAL ',' Maréchal '),' ST ',' Saint '),' STE ',' Sainte '),' PDT ',' Président '),' HT ',' Haut '),' HTE ',' Haute '),' VX ',' Vieux '),' PTE ',' Petite '),'\"',''),'’',chr(39)),
--                          'postcode',
--                          coalesce(cp.postal_code, min(lp.cp)),
--                          'post_office',
--                          CASE WHEN replace(lower(cp.name),'-',' ') != replace(lower(c.name),'-',' ') THEN cp.name ELSE c.name END,
--                          'lat',
--                          round(st_y(st_centroid(st_convexhull(ST_Collect(osm.geometrie))))::numeric,6),
--                          'lon',
--                          round(st_x(st_centroid(st_convexhull(ST_Collect(osm.geometrie))))::numeric,6),
--                          'city',
--                          c.name,
--                          'departement',
--                          cog.nom_dep,
--                          'region',
--                          cog.nom_reg,
--                          'importance',
--                          round(log(c.adm_weight+log(c.population+1)/3)::numeric*log(1+log(count(osm.*)+1)+log(st_length(st_longestline(st_convexhull(ST_Collect(osm.geometrie)),st_convexhull(ST_Collect(osm.geometrie)))::geography)+1)+log(CASE WHEN voie like 'Boulevard%' THEN 4 WHEN voie LIKE 'Place%' THEN 4 WHEN voie LIKE 'Espl%' THEN 4 WHEN voie LIKE 'Av%' THEN 3 WHEN voie LIKE 'Rue %' THEN 2 ELSE 1 END))::numeric,4),
--                          'housenumbers',
--                          translate((json_agg(json_build_object(numero,json_build_object('lon',st_x(osm.geometrie),'lat',st_y(osm.geometrie))))::text),'[]',''))
SELECT osm_postal.fantoir,-- || CASE WHEN coalesce(osm_postal.code_postal, lp.cp)!=lp.cp THEN ('_' || osm_postal.code_postal) ELSE '' END as id,
       osm_postal.insee_com as citycode,
       'street' as type,
       replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(voie,'^IMP ','Impasse '),'^RTE ','Route '),'^ALL ','Allée '),'^PL ','Place '),'^PLA ','Place '),'^AV ','Avenue '),'^LOT ','Lotissement '),'^RES ','Résidence '),'^CHEM ','Chemin '),'^RLE ','Ruelle '),'^BD ','Boulevard '),'^SQ ','Square '),'^PAS ','Passage '),'^SEN ','Sentier '),'^CRS ','Cours '),'^TRA ','Traverse '),'^MTE ','Montée '),'^RPT ','Rond-point '),'^HAM ','Hameau '),'^VLA ','Villa '),'^PROM ','Promenade '),'^ESP ','Esplanade '),'^FG ','Faubourg '),'^TSSE ','Terrasse '),'^CTRE ','Centre '),'^PASS ','Passerelle '),'^FRM ','Ferme '),' GAL ',' Général '),' MAL ',' Maréchal '),' ST ',' Saint '),' STE ',' Sainte '),' PDT ',' Président '),' HT ',' Haut '),' HTE ',' Haute '),' VX ',' Vieux '),' PTE ',' Petite '),'\"',''),'’',chr(39)) AS name,
       osm_postal.code_postal AS postcode,
       --CASE WHEN replace(lower(lp.libelle),'-',' ') != replace(lower(c.name),'-',' ') THEN lp.libelle ELSE c.name END AS post_office,
       round(st_y(st_centroid(st_convexhull(ST_Collect(osm_postal.geometrie))))::numeric,6) AS lat,
       round(st_x(st_centroid(st_convexhull(ST_Collect(osm_postal.geometrie))))::numeric,6) AS lon,
       c.name AS city,
       cog.nom_dep AS departement,
       cog.nom_reg AS region,
       round(log(c.adm_weight+log(c.population+1)/3)::numeric*log(1+log(count(osm_postal.*)+1)+log(st_length(st_longestline(st_convexhull(ST_Collect(osm_postal.geometrie)),st_convexhull(ST_Collect(osm_postal.geometrie)))::geography)+1)+log(CASE WHEN voie like 'Boulevard%' THEN 4 WHEN voie LIKE 'Place%' THEN 4 WHEN voie LIKE 'Espl%' THEN 4 WHEN voie LIKE 'Av%' THEN 3 WHEN voie LIKE 'Rue %' THEN 2 ELSE 1 END))::numeric,4) AS importance,
       --translate((json_agg(json_build_object(numero,json_build_object('lon',st_x(osm_postal.geometrie),'lat',st_y(osm_postal.geometrie))) ORDER BY numero)::text),'[]','') AS housenumbers,
       string_agg(numero||'$'||st_y(osm_postal.geometrie)||'$'||st_x(osm_postal.geometrie),'#' ORDER BY numero)::text AS housenumbers2
       -- "housenumbers":{"1": {"lat": 48.759473,"lon": 2.289989},
FROM v
JOIN infos_communes c
ON (c.insee_com=v.insee_com)
JOIN osm_postal
ON osm_postal.fantoir=v.fantoir
LEFT JOIN cog
ON v.insee_com = cog.insee
--LEFT JOIN codes_postaux lp
--ON (lp.insee=v.insee_com)
--LEFT JOIN polygones_postaux cp
--ON ST_Contains(cp.geometrie, osm.geometrie)
WHERE osm_postal.numero ~ '^[0-9]{1,4}( ?[A-Z]?.*)?' AND
      osm_postal.numero !~'.[0-9 \\.\\-]{9,}' AND
      osm_postal.rang_postal = 1
GROUP BY osm_postal.fantoir,
         osm_postal.insee_com,
         osm_postal.voie,
         osm_postal.code_postal,
--         lp.cp,
         c.name,
--         lp.libelle,
         cog.nom_dep,
         cog.nom_reg,
         c.adm_weight,
         c.population
ORDER BY osm_postal.fantoir;