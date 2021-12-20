WITH
sort_order
AS
(SELECT 1::integer as sortnum, 'OSM' as source
UNION ALL
SELECT 2,'BAL'
UNION ALL
SELECT 3,'CADASTRE'
),
osm
AS
(SELECT geometrie,
        insee_com,
        fantoir,
        ld_bati,
        COALESCE(libelle_osm,libelle_cadastre) libelle,
        code_postal,
        RANK() OVER (PARTITION BY fantoir ORDER BY sortnum) rang
FROM    cumul_places
JOIN    sort_order USING (source)
WHERE   fantoir IS NOT NULL AND
        dept = '__dept__'),
osm_postal
AS
(SELECT o.geometrie,
        o.insee_com,
        o.libelle,
        o.fantoir,
        o.ld_bati,
        COALESCE(o.code_postal,pp.code_postal) code_postal,
        RANK() OVER(PARTITION BY o.fantoir,COALESCE(o.code_postal,pp.code_postal) ORDER BY id) rang_postal
FROM    osm o
JOIN    polygones_postaux pp
ON      ST_Contains(pp.geometrie, o.geometrie)
WHERE   o.rang = 1),
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
SELECT  o.fantoir AS id,
        o.insee_com AS citycode,
        'place' AS type,
	    replace(replace(libelle,'\"',''),'’',chr(39)) AS name,
	    code_postal AS postcode,
        round(st_y(o.geometrie)::numeric,6) AS lat,
        round(st_x(o.geometrie)::numeric,6) AS lon,
        c.name AS city,
        cog.nom_dep AS departement,
        cog.nom_reg AS region,
	    least(0.05,round((log(c.adm_weight+log(c.population+1)/3)*(0.25+0.5*(1- coalesce(o.ld_bati,1))))::numeric,4)) AS importance
FROM    osm_postal o
JOIN    infos_communes c
ON      (c.insee_com=o.insee_com)
JOIN    cog
ON      o.insee_com = cog.insee
WHERE   o.rang_postal = 1
ORDER BY 1;

--least(0.05,round(log((CASE WHEN g.statut LIKE 'Capital%' THEN 6 WHEN g.statut = 'Préfecture de régi' THEN 5 WHEN g.statut='Préfecture' THEN 4 WHEN g.statut LIKE 'Sous-pr%' THEN 3 WHEN g.statut='Chef-lieu canton' THEN 2 ELSE 1 END)+log(g.population+1)/3)*(0.25+0.5*(1-('0' || coalesce(f.ld_bati,'1'))::numeric)),4))