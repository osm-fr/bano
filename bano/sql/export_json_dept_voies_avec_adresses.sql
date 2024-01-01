SELECT fantoir AS id,
       code_insee AS citycode,
       'street' AS type,
       REPLACE(REPLACE(REGEXP_REPLACE(nom_voie,'\t',' '),'"',chr(39)),'’',chr(39)) AS name,
       code_postal AS postcode,
       ROUND(lat_c::numeric,6)::float AS lat,
       ROUND(lon_c::numeric,6)::float AS lon,
       nom_com AS city,
       nom_dep AS departement,
       nom_reg AS region,
       ROUND(LOG(c.adm_weight+LOG(c.population+1)/3)::numeric*LOG(1+LOG(nombre_adresses+1)+LOG(longueur_max+1)+LOG(CASE WHEN nom_voie like 'Boulevard%' THEN 4 WHEN nom_voie LIKE 'Place%' THEN 4 WHEN nom_voie LIKE 'Espl%' THEN 4 WHEN nom_voie LIKE 'Av%' THEN 3 WHEN nom_voie LIKE 'Rue %' THEN 2 ELSE 1 END))::numeric,4)::float AS importance,
       string_agg(numero||'$'||ROUND(ne.lat::numeric,6)::text||'$'||ROUND(ne.lon::numeric,6)::text,'@' ORDER BY numero) AS housenumbers
FROM   (SELECT *
       FROM    numeros_export
       WHERE   dep = '__dept__') ne
JOIN   cog_pyramide_admin
USING  (code_insee)
JOIN   (SELECT fantoir,
               lon AS lon_c,
               lat AS lat_c
       FROM    bano_points_nommes
       WHERE   code_dept = '__dept__') pn
USING  (fantoir)
JOIN   infos_communes c
USING  (code_insee)
JOIN   (SELECT fantoir,
               longueur_max,
               nombre_adresses
       FROM    numeros_export_importance
       WHERE   dep = '__dept__') nimp
USING  (fantoir)
GROUP BY 1,2,3,4,5,6,7,8,9,10,11
ORDER BY 1

limit 50;