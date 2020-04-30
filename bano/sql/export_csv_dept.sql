--SELECT * 
--FROM (
WITH
u
AS 
(SELECT  insee_com,
         fantoir, 
         REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REGEXP_REPLACE(UPPER(numero),'^0*',''),'BIS','B'),'TER','T'),'QUATER','Q'),'QUAT','Q'),' ',''),'à','-'),';',',') AS num 
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
         UPPER(REPLACE(CASE
                          WHEN u.num=o.num THEN o.numero
                          WHEN u.num=od.num THEN od.numero
                          ELSE c.numero
                       END,' ','')) AS numero,
         REPLACE(REPLACE(REGEXP_REPLACE(REGEXP_REPLACE(COALESCE(CASE 
                                                                  	WHEN u.num=o.num THEN
                                                                    CASE 
                                                                        WHEN o.voie_osm != '' THEN REPLACE(o.voie_osm,'’',CHR(39))
                                                                        ELSE o.voie_cadastre
                                                                    END
                                                                    WHEN u.num=od.num THEN
                                                                    CASE
                                                                        WHEN od.voie_osm IS NOT NULL THEN REPLACE(od.voie_osm,'’',CHR(39))
                                                                        ELSE od.voie_cadastre
                                                                    END
                                                                    ELSE
                                                                    CASE
                                                                        WHEN c.voie_osm!='' THEN REPLACE(c.voie_osm,'’',CHR(39))
                                                                        ELSE c.voie_cadastre
                                                                    END
                                                                END,
                                                                CASE
                                                                    WHEN u.num=o.num THEN REPLACE(o.voie_osm,'’',CHR(39))
                                                                    ELSE 
                                                                    CASE
                                                                        WHEN c.voie_osm !='' THEN REPLACE(c.voie_osm,'’',CHR(39))
                                                                        ELSE c.voie_cadastre
                                                                    END
                                                                END),
                                                    '([dD][eé]partementale?|Rue|[rR]urale?|[vV]icinale?|[cC]ommunale?|Cr) ([0-9]+ )?[dD]ite? ',''),
                                                    '(Draille|Chemin|Sentier) [dD]ite? ','1 '),
                                                    'Voie Che ','Chemin '),
                                                    'Cours Dit Che ','Chemin ') AS voie, 
        COALESCE(cp.postal_code, lp.cp, ca.code_postal) AS code_post,
        COALESCE(cn.libelle,initcap(ca.nom_com)) AS ville, 
        CASE 
            WHEN u.num=o.num THEN 'OSM' 
            WHEN (u.num=od.num AND od.voie_osm != od.voie_cadastre AND od.voie_osm IS NOT NULL) THEN 'O+O' 
            WHEN u.num=od.num THEN 'OD' 
            WHEN c.voie_osm != '' THEN 'C+O' 
            ELSE 'CAD' 
        END AS SOURCE, 
        CASE 
            WHEN u.num=o.num THEN st_y(o.geometrie) 
            WHEN u.num=od.num THEN st_y(od.geometrie) 
            ELSE st_y(c.geometrie) 
        END AS lat, 
        CASE 
            WHEN u.num=o.num THEN st_x(o.geometrie) 
            WHEN u.num=od.num THEN st_x(od.geometrie) 
            ELSE st_x(c.geometrie) 
        END AS lon, 
        CASE 
            WHEN u.num=o.num THEN o.geometrie 
            WHEN u.num=od.num THEN od.geometrie 
            ELSE c.geometrie 
        END AS geom 
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
ON (cp."ref:INSEE" = u.insee_com AND ST_Contains(cp.way, COALESCE(o.geometrie, od.geometrie, c.geometrie))) 
WHERE u.num>'0')
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
