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
SELECT osm_postal.fantoir,
       osm_postal.insee_com as citycode,
       'street' as type,
       replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(voie,'^IMP ','Impasse '),'^RTE ','Route '),'^ALL ','Allée '),'^PL ','Place '),'^PLA ','Place '),'^AV ','Avenue '),'^LOT ','Lotissement '),'^RES ','Résidence '),'^CHEM ','Chemin '),'^RLE ','Ruelle '),'^BD ','Boulevard '),'^SQ ','Square '),'^PAS ','Passage '),'^SEN ','Sentier '),'^CRS ','Cours '),'^TRA ','Traverse '),'^MTE ','Montée '),'^RPT ','Rond-point '),'^HAM ','Hameau '),'^VLA ','Villa '),'^PROM ','Promenade '),'^ESP ','Esplanade '),'^FG ','Faubourg '),'^TSSE ','Terrasse '),'^CTRE ','Centre '),'^PASS ','Passerelle '),'^FRM ','Ferme '),' GAL ',' Général '),' MAL ',' Maréchal '),' ST ',' Saint '),' STE ',' Sainte '),' PDT ',' Président '),' HT ',' Haut '),' HTE ',' Haute '),' VX ',' Vieux '),' PTE ',' Petite '),'\"',''),'’',chr(39)) AS name,
       osm_postal.code_postal AS postcode,
       round(st_y(st_centroid(st_convexhull(ST_Collect(osm_postal.geometrie))))::numeric,6) AS lat,
       round(st_x(st_centroid(st_convexhull(ST_Collect(osm_postal.geometrie))))::numeric,6) AS lon,
       c.name AS city,
       cog.nom_dep AS departement,
       cog.nom_reg AS region,
       round(log(c.adm_weight+log(c.population+1)/3)::numeric*log(1+log(count(osm_postal.*)+1)+log(st_length(st_longestline(st_convexhull(ST_Collect(osm_postal.geometrie)),st_convexhull(ST_Collect(osm_postal.geometrie)))::geography)+1)+log(CASE WHEN voie like 'Boulevard%' THEN 4 WHEN voie LIKE 'Place%' THEN 4 WHEN voie LIKE 'Espl%' THEN 4 WHEN voie LIKE 'Av%' THEN 3 WHEN voie LIKE 'Rue %' THEN 2 ELSE 1 END))::numeric,4) AS importance,
       string_agg(numero||'$'||st_y(osm_postal.geometrie)||'$'||st_x(osm_postal.geometrie),'#' ORDER BY numero)::text AS housenumbers2
FROM v
JOIN infos_communes c
ON (c.insee_com=v.insee_com)
JOIN osm_postal
ON osm_postal.fantoir=v.fantoir
LEFT JOIN cog
ON v.insee_com = cog.insee
WHERE osm_postal.numero ~ '^[0-9]{1,4}( ?[A-Z]?.*)?' AND
      osm_postal.numero !~'.[0-9 \\.\\-]{9,}' AND
      osm_postal.rang_postal = 1
GROUP BY osm_postal.fantoir,
         osm_postal.insee_com,
         osm_postal.voie,
         osm_postal.code_postal,
         c.name,
         cog.nom_dep,
         cog.nom_reg,
         c.adm_weight,
         c.population
ORDER BY osm_postal.fantoir;