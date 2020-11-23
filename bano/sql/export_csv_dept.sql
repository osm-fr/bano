--SELECT * 
--FROM (
WITH
u
AS 
(SELECT  insee_com,
         fantoir, 
         REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REGEXP_REPLACE(UPPER(numero),'^0*',''),'BIS','B'),'TER','T'),'QUATER','Q'),'QUAT','Q'),' ',''),'à','-'),';',','),'"','') AS num 
FROM     cumul_adresses 
WHERE    fantoir IS NOT NULL AND
         dept = '__dept__' 
GROUP BY 1,2,3),
lp
AS
(SELECT  insee,
         MIN(cp) AS cp
FROM     codes_postaux
WHERE    insee LIKE '__dept__%'
GROUP BY 1),
res
AS
(SELECT   CONCAT(u.fantoir,'-',u.num) AS id,
         UPPER(REPLACE(COALESCE(o.numero,od.numero,c.numero),' ','')) AS numero,
         REPLACE(
          REPLACE(
            REPLACE(
              REPLACE(
                REPLACE(
                  REGEXP_REPLACE(
                    REGEXP_REPLACE(
                      COALESCE(REPLACE(o.voie_osm,'’',CHR(39)),REPLACE(od.voie_osm,'’',CHR(39)),REPLACE(c.voie_osm,'’',CHR(39)),od.voie_autre,c.voie_autre),
                    '([dD][eé]partementale?|Rue|[rR]urale?|[vV]icinale?|[cC]ommunale?|Cr) ([0-9]+ )?[dD]ite? ',''),
                  '(Draille|Chemin|Sentier) [dD]ite? ','1 '),
                'Voie Che ','Chemin '),
              'Cours Dit Che ','Chemin '),
            '"',CHR(39)), 
          ', ',' '), 
        ',',' ') AS voie, 
        COALESCE(cp.postal_code, lp.cp, ca.code_postal) AS code_post,
        COALESCE(cn.libelle,initcap(ca.nom_com)) AS ville, 
        CASE 
            WHEN u.num=o.num THEN 'OSM' 
            WHEN (u.num=od.num AND od.voie_osm != od.voie_cadastre AND od.voie_osm IS NOT NULL) THEN 'O+O' 
            WHEN u.num=od.num THEN 'OD' 
            WHEN c.voie_osm != '' THEN 'C+O' 
            ELSE 'CAD' 
        END AS SOURCE, 
        COALESCE(st_y(o.geometrie),st_y(od.geometrie),st_y(c.geometrie)) AS lat, 
        COALESCE(st_x(o.geometrie),st_x(od.geometrie),st_x(c.geometrie)) AS lon, 
        COALESCE(o.geometrie,od.geometrie,c.geometrie) AS geom 
FROM u 
LEFT JOIN lp
ON (lp.insee= u.insee_com) 
LEFT JOIN 
(SELECT *, 
        REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REGEXP_REPLACE(UPPER(numero),'^0*',''),'BIS','B'),'TER','T'),'QUATER','Q'),'QUAT','Q'),' ',''),'à','-'),';',',') AS num 
FROM    cumul_adresses 
WHERE   dept = '__dept__' AND
        source = 'OSM') AS o 
ON   (u.num = o.num AND u.fantoir = o.fantoir) 
LEFT JOIN 
(SELECT *, 
        REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REGEXP_REPLACE(UPPER(numero),'^0*',''),'BIS','B'),'TER','T'),'QUATER','Q'),'QUAT','Q'),' ',''),'à','-'),';',',') AS num 
FROM    cumul_adresses 
WHERE   dept = '__dept__' AND
        source = 'CADASTRE' AND
        st_x(geometrie)!=0  AND
        st_y(geometrie)!=0) AS c 
ON (c.num=u.num AND c.fantoir=u.fantoir) 
LEFT JOIN 
(SELECT *, 
        REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REGEXP_REPLACE(UPPER(numero),'^0*',''),'BIS','B'),'TER','T'),'QUATER','Q'),'QUAT','Q'),' ',''),'à','-'),';',',') AS num 
FROM cumul_adresses 
WHERE dept = '__dept__' AND
      source LIKE 'OD%' AND
      st_x(geometrie)!=0 AND
      st_y(geometrie)!=0) AS od 
ON (od.num = u.num AND od.fantoir = u.fantoir) 
LEFT JOIN code_cadastre ca 
ON (ca.insee_com = u.insee_com) 
LEFT JOIN cog_commune cn 
ON (cn.com = u.insee_com) 
LEFT JOIN planet_osm_postal_code cp 
ON (cp."ref:INSEE" = u.insee_com AND ST_Contains(cp.way, ST_Transform(COALESCE(o.geometrie, od.geometrie, c.geometrie),3857))) 
WHERE u.num>'0' AND
      cn.typecom != 'COMD')
SELECT id,
       numero,
       voie,
       code_post,
       ville,
       source,
       lat,
       lon,
       geom
FROM res
WHERE lat IS NOT NULL AND
      lon IS NOT NULL AND
      numero ~ '^[0-9]{1,4}( ?[A-Z]?.*)?' AND
      numero !~'.[0-9 .-]{9,}' 
ORDER BY id
