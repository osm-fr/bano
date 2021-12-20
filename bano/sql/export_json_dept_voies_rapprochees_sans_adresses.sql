WITH
set_fantoir
AS
(SELECT fantoir FROM cumul_voies WHERE dept = '__dept__' AND COALESCE(fantoir,'') != ''
EXCEPT
SELECT fantoir FROM cumul_adresses WHERE dept = '__dept__'),
osm_postal
AS
(SELECT v.geometrie,
        insee_com,
        fantoir,
        REPLACE(REPLACE(REGEXP_REPLACE(v.voie_osm,'\t',' '),'"',chr(39)),'’',chr(39)) AS name,
        pp.code_postal,
        RANK() OVER(PARTITION BY v.fantoir ORDER BY id) rang_postal
FROM    cumul_voies v
JOIN    set_fantoir
USING   (fantoir)
JOIN    polygones_postaux pp
ON      ST_Contains(pp.geometrie, v.geometrie)),
cog
AS
(SELECT cc.com AS insee,
        cd.libelle AS nom_dep,
        cr.libelle AS nom_reg
FROM    cog_commune cc
JOIN    cog_departement cd
USING   (dep)
JOIN    cog_region cr
ON      cc.reg = cr.reg
WHERE   cc.dep = '__dept__')
SELECT  p.fantoir,
        p.insee_com AS citycode,
        'street' AS type,
        p.name,
        p.code_postal AS postcode,
        round(st_y(p.geometrie)::numeric,6) AS lat,
        round(st_x(p.geometrie)::numeric,6) AS lon,
        c.name AS city,
        cog.nom_dep AS departement,
        cog.nom_reg AS region,
        round(log(c.adm_weight+log(c.population+1)/3)::numeric*log(1+log(count(p.*)+1)+log(CASE WHEN p.name like 'Boulevard%' THEN 4 WHEN p.name LIKE 'Place%' THEN 4 WHEN p.name LIKE 'Espl%' THEN 4 WHEN p.name LIKE 'Av%' THEN 3 WHEN p.name LIKE 'Rue %' THEN 2 ELSE 1 END))::numeric,4) AS importance
FROM    osm_postal p
JOIN    infos_communes c
USING   (insee_com)
LEFT JOIN cog
ON      p.insee_com = cog.insee
WHERE    p.rang_postal = 1
GROUP BY p.fantoir,
         p.insee_com,
         p.code_postal,
         p.name,
         p.geometrie,
         c.name,
         cog.nom_dep,
         cog.nom_reg,
         c.adm_weight,
         c.population
ORDER BY p.fantoir;

